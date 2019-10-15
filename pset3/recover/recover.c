#include <stdio.h>
#include <stdlib.h>

int main(int argc, char *argv[])
{
    // ensure proper usage of main function
    if (argc != 2)
    {
        printf("Usage: ./recover image\n");
        return 1;
    }

    // define filename
    char *infile = argv[1];

    // open infile
    FILE *inptr = fopen(infile, "r");

    // ensure correct infile format
    if (inptr == NULL)
    {
        printf("Could not open %s", infile);
        return 2;
    }

    // allocate memory for buffer of 512 bytes
    unsigned char buffer[512];

    // define image no. and filename
    int n = 0;
    FILE *img = NULL;

    // loop through inptr and find jpg's
    while (fread(buffer, 512, 1, inptr))
    {
        // jpg condition
        if (buffer[0] == 0xff &&
            buffer[1] == 0xd8 &&
            buffer[2] == 0xff &&
            (buffer[3] & 0xf0) == 0xe0)
        {
            if (n > 0)
            {
                fclose(img);
            }

            // make new  filename
            char filename[8];
            sprintf(filename, "%03i.jpg", n);

            // open image in 'write' mode
            img = fopen(filename, "w");
            if (!img)
            {
                printf("Could not create %s.\n", filename);
                free(buffer);
                return 3;
            }

            // add to 'n' for next filename
            n++;

        }

        // write to a jpg if it exists
        if (img != NULL)
        {
            fwrite(buffer, 512, 1, img);
        }
    }

    // close images
    fclose(inptr);
    fclose(img);
    return 0;
}