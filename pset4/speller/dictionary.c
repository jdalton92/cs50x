// Implements a dictionary's functionality

#include <ctype.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "dictionary.h"

// Represents number of buckets in a hash table
#define N 26

// Represents a node in a hash table
typedef struct node
{
    char word[LENGTH + 1];
    struct node *next;
}
node;

// Represents a hash table
node *hashtable[N];

// Hashes word to a number between 0 and 25, inclusive, based on its first letter
unsigned int hash(const char *word)
{
    return tolower(word[0]) - 'a';
}

// variable to count size of dictionary
int dict_size = 0;

// Loads dictionary into memory, returning true if successful else false
bool load(const char *dictionary)
{
    // Initialize hash table
    for (int i = 0; i < N; i++)
    {
        hashtable[i] = NULL;
    }

    // Open dictionary
    FILE *file = fopen(dictionary, "r");
    if (file == NULL)
    {
        unload();
        return false;
    }

    // Buffer for a word
    char word[LENGTH + 1];

    // Insert words into hash table
    while (fscanf(file, "%s", word) != EOF)
    {

        dict_size ++;

        // create temp node with check
        node *new_node = malloc(sizeof(node));
        if (new_node == NULL)
        {
            unload();
            return false;
        }

        // copy word into node
        strcpy(new_node->word, word);

        // find index for word
        int index = hash(word);

        // if list is empty then create list with word
        if (hashtable[index] == NULL)
        {
            hashtable[index] = new_node;
            new_node->next = NULL;
        }

        // if list isn't empty then add to list
        else
        {
            // point new_node to first item in list
            new_node->next = hashtable[index];
            hashtable[index] = new_node;
        }
    }

    // Close dictionary
    fclose(file);

    // Indicate success
    return true;
}

// Returns number of words in dictionary if loaded else 0 if not yet loaded
unsigned int size(void)
{
    // if dictionary loaded, return size else 0
    if (dict_size)
    {
        return dict_size;
    }
    else
    {
        return 0;
    }
}

// Returns true if word is in dictionary else false
bool check(const char *word)
{
    // store temp variable for lower case word
    char tmp[LENGTH + 1];
    // find length of word
    int len = strlen(word);
    // convert word to lower case
    for (int i = 0; i < len; i++)
    {
        tmp[i] = tolower(word[i]);
    }
    // end word with '\0' so computer knows it is end of string
    tmp[len] = '\0';

    // get index of lower case word in hashtable
    int index = hash(tmp);

    // create cursor that goes through a list in the hashtable
    node *cursor = hashtable[index];

    // return false if hashtable empty
    if (hashtable[index] == NULL)
    {
        return false;
    }

    // Go through linked list and compare words
    while (cursor != NULL)
    {
        if (strcmp(tmp, cursor->word) == 0)
        {
            return true;
        }

        cursor = cursor->next;
    }

    // else return false if word not found
    return false;
}

// Unloads dictionary from memory, returning true if successful else false
bool unload(void)
{
    // go through hashtable and free memory
    for (int i = 0; i < N; i++)
    {
        // create cursor to go through linked list
        node *cursor = hashtable[i];

        while (cursor != NULL)
        {
            node *tmp = cursor;
            cursor = cursor->next;
            free(tmp);
        }

    }

    // return true on success
    return true;
}
