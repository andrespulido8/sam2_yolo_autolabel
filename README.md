# SAM2 Video Autolabel

This repository contains utilities for automatically labeling videos by processing them into frames and applying various image processing techniques.

The following image is an example of the output of the utilities in this repository:

![Example Output](images/yolo_bbox_output.png)


## Installation

To use these utilities, you need to have the `sam2` repository cloned in your system. You can clone the repository using the following command:

```sh
git clone https://github.com/facebookresearch/sam2.git
```
Follow the instructions in the [`sam2`] repository to set up the environment and install the required dependencies.

Then, clone this repository in the notebook directory of the `sam2` repository. 

Additionally, you need to have [`ffmpeg`]

```sh
sudo apt-get install ffmpeg
```

## Usage

### Placing and Formatting Data

1. **Extracting Frames from Video**:
    - Ensure your video is in a supported format (e.g., `.mp4`).
    - Extract JPEG frames from your video using [`ffmpeg`]
      ```sh
      ffmpeg -i <your_video>.mp4 -r 2 -q:v 2 -start_number 0 <output_dir>/'%05d.jpg'
      ```
      - `-r 2`: Extracts 2 frames per second.
      - `-q:v 2`: Generates high-quality JPEG frames.
      - `-start_number 0`: Starts the JPEG filenames from `00000.jpg`.

2. **Directory Structure**:
    - Place the extracted frames in a directory under the [`videos`] directory in the `sam2` repository with an appropiate name (we are using the standard `<date>_<location>_<description>`, for example `20241003_autonomy_park_big_dog`). 

3. **Split images into batches**
    - If you have a large number of images (which we normally do have ~>300), you can split them into batches using the following command:
      ```sh
      python image_utils.py -f split_batches 
      ```
    - First make sure the directory and the batch size is set in the `image_utils.py` file.

4. **Labeling the Data**:
    - Use the [`sam2_video_autolabel.ipynb`] notebook to label the data.

5. **Combining the Batches**:
    - After labeling the data, you can combine the batches using the following command:
      ```sh
      python image_utils.py -f join_batches 
      ```
    - First make sure the directory and the batch size is set in the `image_utils.py` file.

6. (for RAITE) **Upload images and labels to Dropbox**:

### Running the Notebook

**Open the Notebook**:
    - Open the [`sam2_video_autolabel.ipynb`] with either Jupyter Notebook with 
        ```sh
        jupyter notebook
        ```
    - Or open it in VSCode with the Python extension installed by following [these instructions](https://code.visualstudio.com/docs/datascience/jupyter-notebooks).

## License

This project is licensed under the MIT License. See the LICENSE file for details.
