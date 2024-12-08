# SDTagSearch
A GUI application to search for StableDiffusion images that match specified generation tags.

This was made to work with ComfuiUI-generated images.
This also only works if your prompt conditioning node is node number 6, but I might change this later. Right now it finds the prompt by converting the metadata to a dict and finding the text in node 6, but I might have to use regex to find the prompt in the future.

This code was frankensteined from a few other smaller projects I had so don't judge the code too much 💀

# Usage
1. Download `main.py`
2. Modify `input_dir` (line 7) to the directory with your StableDiffusion generated images
3. Run the code
