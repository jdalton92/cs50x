// Copies a BMP file

#include <stdio.h>
#include <stdlib.h>

#include "bmp.h"

int main(int argc, char *argv[])
{
    // ensure proper usage
    if (argc != 4)
    {
        fprintf(stderr, "Usage: ./resize n infile outfile\n");
        return 1;
    }

    // remember the resize factor
    int n = atoi(argv[1]);

    // remember filenames
    char *infile = argv[2];
    char *outfile = argv[3];

    // open input file
    FILE *inptr = fopen(infile, "r");
    if (inptr == NULL)
    {
        fprintf(stderr, "Could not open %s.\n", infile);
        return 2;
    }

    // open output file
    FILE *outptr = fopen(outfile, "w");
    if (outptr == NULL)
    {
        fclose(inptr);
        fprintf(stderr, "Could not create %s.\n", outfile);
        return 3;
    }

    // read infile's BITMAPFILEHEADER
    BITMAPFILEHEADER bf;
    fread(&bf, sizeof(BITMAPFILEHEADER), 1, inptr);

    // read infile's BITMAPINFOHEADER
    BITMAPINFOHEADER bi;
    fread(&bi, sizeof(BITMAPINFOHEADER), 1, inptr);

    // ensure infile is (likely) a 24-bit uncompressed BMP 4.0
    if (bf.bfType != 0x4d42 || bf.bfOffBits != 54 || bi.biSize != 40 ||
        bi.biBitCount != 24 || bi.biCompression != 0)
    {
        fclose(outptr);
        fclose(inptr);
        fprintf(stderr, "Unsupported file format.\n");
        return 4;
    }

    // get new dimensions for resized image
    int width = bi.biWidth;
    int height = bi.biHeight;

    // reconfigure header pt 1
    BITMAPFILEHEADER resize_bf = bf;
    BITMAPINFOHEADER resize_bi = bi;
    resize_bi.biWidth *= n;
    resize_bi.biHeight *= n;

    // find padding for scanlines
    int inPadding = (4 - (width * sizeof(RGBTRIPLE)) % 4) % 4;
    int outPadding = (4 - (resize_bi.biWidth * sizeof(RGBTRIPLE)) % 4) % 4;

    // reconfigure header pt 2
    resize_bi.biSizeImage = ((resize_bi.biWidth * sizeof(RGBTRIPLE)) + outPadding) * abs(resize_bi.biHeight);
    resize_bf.bfSize = resize_bi.biSizeImage + sizeof(BITMAPFILEHEADER) + sizeof(BITMAPINFOHEADER);

    // write outfile's BITMAPFILEHEADER
    fwrite(&resize_bf, sizeof(BITMAPFILEHEADER), 1, outptr);

    // write outfile's BITMAPINFOHEADER
    fwrite(&resize_bi, sizeof(BITMAPINFOHEADER), 1, outptr);

    // temporary storage
    RGBTRIPLE scanline[resize_bi.biWidth];

    // iterate over infile's scanlines
    for (int i = 0, biHeight = abs(height); i < biHeight; i++)
    {
        // iterate over pixels in a scanline
        for (int j = 0; j < width; j++)
        {
            // temporary storage
            RGBTRIPLE triple;

            // read RGB triple from infile
            fread(&triple, sizeof(RGBTRIPLE), 1, inptr);

            // new scanline
            for (int k = 0; k < n; k++)
            {
                scanline[(j * n) + k] = triple;
            }
        }

        // skip over padding, if any
        fseek(inptr, inPadding, SEEK_CUR);

        // write the current scanline 'n' times
        for (int j = 0; j < n; j++)
        {
            // write a new scanline
            fwrite(scanline, sizeof(RGBTRIPLE), resize_bi.biWidth, outptr);

            // add back padding
            for (int k = 0; k < outPadding; k++)
            {
                fputc(0x00, outptr);
            }
        }
    }

    // close infile
    fclose(inptr);

    // close outfile
    fclose(outptr);

    // success
    return 0;
}