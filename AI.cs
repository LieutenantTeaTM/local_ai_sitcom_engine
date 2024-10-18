using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.AI; // Important

public class AI : MonoBehaviour
{
    // This is all optional, use if you want random wander AI for your characters, I just like it!
    
    // Be sure to build NavMesh on your scene! And add NavMesh Agents to your characters

    // Wander AI for the characters
    // Radius in which they can move
    public float wanderRadius;
    // Time until they can move again
    public float wanderTimer;

    // The agent on the character, we put this script on every character
    private NavMeshAgent agent;
    // Local timer to wait
    private float timer;

    // Use this for initialization
    void OnEnable()
    {
        // Grab the agent component you set
        agent = GetComponent<NavMeshAgent>();
        // Initially set the timer to the base wait time
        timer = wanderTimer;
    }

    void Update()
    {
        // Add to the local timer infinitely
        timer += Time.deltaTime;

        // Check if the timer is greater than the base waiting time
        if (timer >= wanderTimer)
        {
            // Basically, pick a random direction and go there lmao
            Vector3 newPos = RandomNavSphere(transform.position, wanderRadius, -1);
            agent.SetDestination(newPos);
            // Reset the timer so we can wait again
            timer = 0;
        }
    }

    public static Vector3 RandomNavSphere(Vector3 origin, float dist, int layermask)
    {
        // Get a random unit in a sphere
        Vector3 randDirection = Random.insideUnitSphere * dist;

        randDirection += origin;

        NavMeshHit navHit;

        // Change the direction and go there
        NavMesh.SamplePosition(randDirection, out navHit, dist, layermask);

        return navHit.position;
    }
}
