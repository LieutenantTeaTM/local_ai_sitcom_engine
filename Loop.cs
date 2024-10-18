using System.Collections;
using System.Collections.Generic;
using System.IO;
using UnityEngine;
using UnityEngine.Networking;
using System.Linq;
using TMPro;
using UnityEngine.Video;

public class Loop : MonoBehaviour
{
    // This is where a lot of magic happens from our Python engine
    
    // Stores the dialogue line index matched with the dialoue line, the audio data, and the name of the character
    private Dictionary<int, (string text, AudioClip clip, string name)> audioData =
        new Dictionary<int, (string, AudioClip, string)>();

    // If you want background music for your sitcom
    public AudioSource musicPlayer;
    // An array of possible music if you want random music per 'episode'
    public AudioClip[] musicClipChoice;
    // Mandatory audio source that hosts all the voices and dynamically changes them per line
    // Also can be set to 2D in Unity
    public AudioSource voicePlayer;

    // Ideally change to a full path otherwise it seems to fail
    // You need an 'Audio' folder for the Python engine
    // Also you may need to create StreamingAssets manually
    public string audioFolderPath = Path.GetFullPath("StreamingAssets/Audio");
    public string textFilePath = Path.GetFullPath("StreamingAssets/lines.txt");  // The file from the python engine
    // The dialogue TextMeshPro text
    // Technically optional but highly recommended
    [SerializeField] TextMeshProUGUI dialogue;
    // List of colors if you want the text to be different colors based on the character
    public Color[] characterColors;

    // Things for infinitely looping
    private bool isProcessing = false;  // Tracks if audio is being processed
    private bool keepRunning = true;    // Controls the infinite loop

    // Videos for Spongebob-like transitions i.e. "12 hours later" or "1 eternity later"
    // Also has the UI element as a gameobject, which are separat objects!
    public VideoPlayer waitingMovie; public GameObject UIMovie;
    
    // Viewer waiting movie, optional, but pretty cool
    // This is what plays when the python engine is working on the background
    // You can add nice waiting music and animations because it sure takes a while
    public VideoPlayer transitionMovie; public GameObject UITransition;

    // For the camera
    public Transform currentTarget;   // Current character to follow
    public Vector3 offset = new Vector3(0, 5, -10); // Offset from the target
    public float followSpeed = 5f;    // Speed of following the target
    public float lookSpeed = 5f;      // Speed of looking at the target
    public float transitionDuration = 1f; // Duration of the character transition

    private Transform nextTarget;     // The next character to transition to
    private float transitionProgress = 0f;
    private bool isTransitioning = false;

    public GameObject camObj;

    // Character transforms
    public Transform sponge; public Transform pat;

    private void Start()
    {
        // Stop all of the data so we can immediately jump in the first scene
        musicPlayer.Stop();
        transitionMovie.Stop();
        UITransition.SetActive(false);
        // If you have random music you choose a random clip here
        musicPlayer.clip = musicClipChoice[Random.Range(0, musicClipChoice.Length)];
        // Play the random music
        musicPlayer.Play();
        waitingMovie.Stop();
        UIMovie.SetActive(false);
        // Start the infinite loop
        StartCoroutine(InfiniteAudioLoop());
    }

    private void LateUpdate()
    {
        if (isTransitioning)
        {
            SmoothTransition();
        }
        else
        {
            FollowTarget();
            FaceCharacterForward();
        }
    }

    private void FollowTarget()
    {
        // Smoothly move to the target's position plus the offset
        Vector3 desiredPosition = currentTarget.position + offset;
        camObj.transform.position = Vector3.Lerp(camObj.transform.position, desiredPosition, followSpeed * Time.deltaTime);
    }
    
    public void TransitionToTarget(Transform newTarget)
    {
        // Start transitioning to a new character
        nextTarget = newTarget;
        isTransitioning = true;
        transitionProgress = 0f;
    }

    private void SmoothTransition()
    {
        // Progress the transition over time
        transitionProgress += Time.deltaTime / transitionDuration;

        // Smoothly interpolate position and rotation
        Vector3 newPosition = Vector3.Lerp(camObj.transform.position, nextTarget.position + offset, transitionProgress);
        camObj.transform.position = newPosition;

        Vector3 direction = (nextTarget.position - camObj.transform.position).normalized;
        Quaternion newRotation = Quaternion.LookRotation(direction);
        camObj.transform.rotation = Quaternion.Slerp(camObj.transform.rotation, newRotation, transitionProgress);

        // End transition when complete
        if (transitionProgress >= 1f)
        {
            currentTarget = nextTarget;
            isTransitioning = false;
        }
    }

    private void FaceCharacterForward()
    {
        // Smoothly rotate the camera to look at the character
        Quaternion targetRotation = Quaternion.LookRotation(currentTarget.position - transform.position);
        transform.rotation = Quaternion.Slerp(transform.rotation, targetRotation, lookSpeed * Time.deltaTime);
    }

    // Infinite loop to continuously process audio files
    private IEnumerator InfiniteAudioLoop()
    {
        // Just run until shutdown
        while (keepRunning)
        {
            // Check if we are processing so it doesn't repeatedly call it, and check if the signal done text file exists so we can wait in the frontend
            if (!isProcessing && !File.Exists(Path.Combine(Application.streamingAssetsPath, "signal_done.txt"))) // Only start if nothing is being processed
            {
                // Begin parsing data
                yield return StartCoroutine(LoadAudioData());
            }
            else
            {
                yield return null; // Wait until the current process completes
            }
        }
    }

    private IEnumerator LoadAudioData()
    {
        // Once again make sure everything stopped
        transitionMovie.Stop();
        UITransition.SetActive(false);
        musicPlayer.Stop();
        // Choose random music every 'episode'
        musicPlayer.clip = musicClipChoice[Random.Range(0, musicClipChoice.Length)];
        musicPlayer.Play();
        waitingMovie.Stop();
        UIMovie.SetActive(false);
        // Tell the main loop we are processing and don't run this again
        isProcessing = true;
        
        // Read text content and parse it
        string[] lines = File.ReadAllLines(Path.Combine(Application.streamingAssetsPath, textFilePath));

        // Increment by 2 because of how Python generated our script, so we check two lines at a time
        for (int i = 0; i < lines.Length; i += 2)
        {
            // Gather every other line
            int index = int.Parse(lines[i]);
            string content = lines[i + 1];
            // Dummy value for a character name
            string name = "";

            // Dummy value for audioPath
            string audioPath = "";
            // Load the corresponding audio file if it is sponge
            if (File.Exists(Path.Combine(Application.streamingAssetsPath, "Audio", $"{index}_sponge.wav")))
            {
                audioPath = Path.Combine(Application.streamingAssetsPath, "Audio", $"{index}_sponge.wav");
                // Set name to sponge for later use
                name = "sponge";
            }

            // Load the corresponding audio file if it is patrick
            if (File.Exists(Path.Combine(Application.streamingAssetsPath, "Audio", $"{index}_pat.wav")))
            {
                audioPath = Path.Combine(Application.streamingAssetsPath, "Audio", $"{index}_pat.wav");
                // Set name to pat for later use
                name = "pat";
            }

            // Make a 'web' request to get StreamingAssets audio
            using (UnityWebRequest www = UnityWebRequestMultimedia.GetAudioClip(audioPath, AudioType.WAV))
            {
                // Shoot a request
                yield return www.SendWebRequest();

                // Check if it's successfull which it should be or something went wrong
                if (www.result == UnityWebRequest.Result.Success)
                {
                    // Add the clip to the audioData dictionary, including the text and character name
                    AudioClip clip = DownloadHandlerAudioClip.GetContent(www);
                    audioData[index] = (content, clip, name);
                }
                else
                {
                    // Alert the user there was an error with the request
                    Debug.LogError($"Failed to load audio");
                }
            }
        }

        // Done loading
        Debug.Log("Audio data loaded.");
        // Start playing audio index by index
        StartCoroutine(PlayAudioSequence());
    }

    private IEnumerator PlayAudioSequence()
    {
        // Debug print all the values
        foreach (var kvp in audioData)
        {
            Debug.Log($"Key: {kvp.Key}, Value: {kvp.Value}");
        }

        // Then play the data one by one
        foreach (var entry in audioData.OrderBy(e => e.Key))
        {
            Debug.Log($"Playing {entry.Key}: {entry.Value.text}");
            // Check who is speaking
            switch (entry.Value.name) {
                case "sponge":
                    // Change the dialogue text to the sponge yellow
                    dialogue.color = characterColors[0];
                    currentTarget = sponge;
                    TransitionToTarget(sponge);
                    // Prefix it with 'sponge' so we can see sponge is talking
                    dialogue.text = "sponge: " + entry.Value.text;
                    break;
                case "pat":
                    // Change the dialogue text to the patrick pink
                    dialogue.color = characterColors[1];
                    currentTarget = pat;
                    TransitionToTarget(pat);
                    // Prefix it with 'pat' so we can see patrick is talking
                    dialogue.text = "pat: " + entry.Value.text;
                    break;
            }
            // Gather the clip audio then play it 
            voicePlayer.clip = entry.Value.clip;
            voicePlayer.Play();

            // Wait until the line is done so they don't overlap
            yield return new WaitForSeconds(entry.Value.clip.length);
        }

        // Notify Python that the sequence is complete
        SignalPython();
    }

    private void SignalPython()
    {
        // Stop random music
        musicPlayer.Stop();

        // Play the 'one eternity later' screen briefly
        UIMovie.SetActive(true);
        waitingMovie.Play();
        Debug.Log("Notifying Python of completion.");

        // Create an empty file that Python listens for
        string signalPath = Path.Combine(Application.streamingAssetsPath, "signal_done.txt");
        
        // Technically not even needed but eh
        // Python and Unity don't check for the text file content
        File.WriteAllText(signalPath, "done");

        // Wait until the 'one eternity later' text is done playing
        StartCoroutine(waitForEnd());
    }

    private IEnumerator waitForEnd()
    {
        audioData.Clear();
        // Wait until the 'one eternity later' text is done playing (about ~3 seconds)
        yield return new WaitForSeconds(3);

        // Start the waiting animation and now Python should start generating the next episode
        UITransition.SetActive(true);
        transitionMovie.Play();
        // We are done processing now the loop can continue
        isProcessing = false;
    }
}
