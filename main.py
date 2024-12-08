import os
from PIL import Image, ImageTk
import json
import tkinter as tk

# Directory containing the PNG files
input_dir = r"C:\Path\To\Files"


def get_tags(img_path): # String
    try:
        image = Image.open(img_path)

        # Get the metadata from the image
        metadata = image.info

        # Get the tags from the metadata
        input_tags = json.loads(metadata["prompt"])["6"]["inputs"]["text"] # This only works if node 6 is the input. Will need to fix later.

        image.close()

        return input_tags
    except Exception as e:
        print(f"[!] No tags found for {img_path} :(")
        print(f"Exception for error above: {e}")
        return ""


def file_iterate(input_dir): # List
    image_paths = []

    # Iterate over each file in the directory
    for filename in os.listdir(input_dir):
        if filename.endswith(".png"):
            file_path = os.path.join(input_dir, filename)
            image_paths.append(file_path)

    return image_paths


def search_images_by_tag(directory, target_tags): # List
    matching_images = []
    
    #Convert string of tags to a list
    target_tags = set([tag.strip().replace(' ', '_').replace('(', '').replace(')', '') for tag in target_tags.split(',')])
    
    all_images = file_iterate(directory)

    for img_path in all_images:
        tags = [tag.strip().replace(' ', '_').replace('(', '').replace(')', '') for tag in get_tags(img_path).split(',')]

        #Adds the current image to the list of matching images if it has all the target tags
        if tags != []:
            tag_set = set(tags)
            if tag_set.issuperset(target_tags):
                matching_images.append(img_path)

    return matching_images



#------------------------------------------------GUI FUNCTIONS----------------------------------------------------#

class SDSearchEngine:

    def __init__(self, input_dir):
        #Declare vars
        self.sd_output_path = input_dir
        self.pages_len = 0
        self.imgs_per_page = 40
        self.imgs_per_row = 4
        self.matching_images = []
        self.current_page = 1

        #Init window
        self.root = tk.Tk()
        self.root.title("SD Results Search Engine")
        self.root.geometry("1200x800")
        self.root.configure(background="#ffffff")

        #Init the button grid at top
        self.menu_grid = tk.Frame(self.root, background="#dddddd")
        self.menu_grid.columnconfigure(0, weight=3)
        self.menu_grid.columnconfigure(1, weight=1)
        self.menu_grid.columnconfigure(2, weight=1)
        self.menu_grid.columnconfigure(3, weight=1)
        self.menu_grid.columnconfigure(4, weight=1)
        self.menu_grid.pack(padx=10, pady=10, fill='x')

        #Init search box
        self.search_box = tk.Entry(self.menu_grid, font=('Arial', 16))
        self.search_box.bind("<Return>", lambda event: self.get_images_with_tags())
        self.search_box.grid(row=0, column=0, padx=0, pady=0, sticky='ew')

        #Init search button
        self.search_button = tk.Button(self.menu_grid, text="Search", font=('Arial', 16), command=self.get_images_with_tags)
        self.search_button.grid(row=0, column=1, padx=0, pady=0, sticky='ew')

        #Init reset button
        self.reset_button = tk.Button(self.menu_grid, text="Reset", font=('Arial', 16), command=self.reset_grid)
        self.reset_button.grid(row=0, column=2, padx=0, pady=0, sticky='ew')

        # Init images per row selector
        self.imgs_per_row_label = tk.Label(self.menu_grid, text="Images per Row:", font=('Arial', 16))
        self.imgs_per_row_label.grid(row=0, column=3, padx=10, pady=0, sticky='e')
        self.imgs_per_row_var = tk.StringVar()
        self.imgs_per_row_var.set(str(self.imgs_per_row))
        self.imgs_per_row_dropdown = tk.OptionMenu(self.menu_grid, self.imgs_per_row_var, "2", "3", "4", "5", "6")
        self.imgs_per_row_dropdown.config(font=('Arial', 16))
        self.imgs_per_row_dropdown.grid(row=0, column=4, padx=0, pady=0, sticky='w')
        self.imgs_per_row_var.trace("w", self.update_imgs_per_row)

        # Init images per page selector
        self.imgs_per_page_label = tk.Label(self.menu_grid, text="Images per Page:", font=('Arial', 16))
        self.imgs_per_page_label.grid(row=0, column=5, padx=10, pady=0, sticky='e')
        self.imgs_per_page_var = tk.StringVar()
        self.imgs_per_page_var.set(str(self.imgs_per_page))
        self.imgs_per_page_dropdown = tk.OptionMenu(self.menu_grid, self.imgs_per_page_var, "20", "40", "60", "80", "100")
        self.imgs_per_page_dropdown.config(font=('Arial', 16))
        self.imgs_per_page_dropdown.grid(row=0, column=6, padx=0, pady=0, sticky='w')
        self.imgs_per_page_var.trace("w", self.update_imgs_per_page)


        #Init scrollbar
        self.scrollbar = tk.Scrollbar(self.root)
        self.scrollbar.pack(side="right", fill="y")

        #Init the canvas
        self.canvas = tk.Canvas(self.root, background="#ffffff")
        self.canvas.pack(fill="both", expand=True) #Add side

        #Configs for scrollbar
        self.scrollbar.configure(command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        #Init the outer grid and set columns
        self.reset_grid()

        #Init the page grid at bottom
        self.reset_pages()

        #Init the canvas window to hold grid
        self.canvas.create_window(0, 0, anchor='nw', window=self.grid_frame, tags="canvwin", width=self.root.winfo_width())

        #Config canvas so scrollbar works
        self.canvas.bind_all("<Configure>", lambda event: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind_all("<MouseWheel>", lambda event: self.canvas.yview_scroll(int(-1 * (event.delta / 60)), "units"))

        #Config to resize canvas when window size changes
        self.canvas.bind("<Configure>", lambda event: self.canvas.itemconfigure("canvwin", width=event.width))

        self.root.mainloop()


    def get_images_with_tags(self):
        self.reset_grid(True) #Clear the grid
        input_tags = self.search_box.get() #Get the input
        print("searching for: {tags}".format(tags=input_tags))

        #Get all matching image file names
        self.matching_images = search_images_by_tag(self.sd_output_path, input_tags)

        #Show error if no matching images...
        if not self.matching_images:
            self.reset_pages(True)
            self.no_results_message = tk.Label(self.grid_frame, text="No images found for \"{tags}\"".format(tags=input_tags), font=('Arial', 16))
            self.no_results_message.grid(row=0, column=0, rowspan=1, columnspan=self.imgs_per_row, sticky='nesw')
            print("No images found for \"{tags}\"".format(tags=input_tags))
        else:
            print("Total images: " + str(len(self.matching_images)))
        
            self.reset_pages(True)
            self.load_page(1)


    def reset_pages(self, *destroy):
        #Clear page button grid
        if destroy:
            self.page_grid.destroy()

        #Get the number of pages
        self.pages_len = (len(self.matching_images) + self.imgs_per_page - 1) // self.imgs_per_page
        print("Images:", len(self.matching_images), "Pages:", self.pages_len)

        #Create the grid again
        self.page_grid = tk.Frame(self.root, bg="#ffffff")
        self.page_grid.pack(padx=0, pady=0, fill='x', side='top')
        self.page_text = tk.Label(self.page_grid, text="Pages: ", font=('Arial', 12), bg="#ffffff")
        self.page_text.grid(row=0, column=0)

        #Create the page buttons
        for page_num in range(self.pages_len):
            page_num += 1
            self.page_button = tk.Button(self.page_grid, text=str(page_num), font=('Arial', 12), command=lambda page=page_num: self.load_page(page))
            self.page_button.grid(row=0, column=page_num)

        self.load_page(self.current_page)


    def load_page(self, page_num):
        self.current_page = page_num

        self.reset_grid(True)
        print("Loading page: " + str(page_num))
        for img_num, image_name in enumerate(self.matching_images[(page_num-1)*self.imgs_per_page : page_num*self.imgs_per_page]):
            print((page_num-1)*self.imgs_per_page+img_num, image_name)
            self.set_grid_image(image_name, img_num)
        #if img_num < 39:
        #   for cell in range(self.imgs_per_page - img_num):
        #       self.set_grid_image(Image.new(size=(0,0), mode="RGB"), img_num+cell+1)
        self.canvas.yview_moveto(0.0)


    def reset_grid(self, *destroy):
        if destroy:
            self.grid_frame.destroy()
        self.grid_frame = tk.Frame(self.canvas, background="#ffffff")
        self.grid_frame.columnconfigure(0, weight=1)
        self.grid_frame.columnconfigure(1, weight=1)
        self.grid_frame.columnconfigure(2, weight=1)
        self.grid_frame.columnconfigure(3, weight=1)
        self.grid_frame.pack(fill='both')
        self.canvas.itemconfigure("canvwin", window=self.grid_frame, width=self.root.winfo_width())
        self.canvas.yview_moveto(0.0)


    def set_grid_image(self, image_path, img_num):
        grid_width = self.canvas.winfo_width() / self.imgs_per_row
        grid_height = grid_width

        # Resize the image to fit the grid square while maintaining aspect ratio
        img = Image.open(image_path)
        img.thumbnail((grid_width, grid_height))
        
        self.photo1 = ImageTk.PhotoImage(img)
        self.img_label = tk.Label(self.grid_frame, image=self.photo1, background="#ffffff", width=grid_width, height=grid_height)
        self.img_label.image = self.photo1
        self.img_label.grid(row=int(img_num / self.imgs_per_row), column=img_num % self.imgs_per_row, rowspan=1, columnspan=1, padx=0, pady=0, sticky='nesw')
        self.img_label.bind("<Button-1>", lambda event,img_name=image_path: self.open_image_info(img_name))


    def update_imgs_per_row(self, *args):
        self.imgs_per_row = int(self.imgs_per_row_var.get())
        self.reset_pages(True)

    def update_imgs_per_page(self, *args):
        self.imgs_per_page = int(self.imgs_per_page_var.get())
        self.reset_pages(True)


    def open_image_info(self, image_name):
        print("Image Clicked:", image_name)
        # Open a new window
        self.image_info_window = tk.Toplevel(self.root)
        self.image_info_window.title("Image Information")
        self.image_info_window.geometry("1200x400")

        self.image_info_frame = tk.Frame(self.image_info_window, background="#ffffff")
        self.image_info_frame.columnconfigure(0, weight=1)
        self.image_info_frame.columnconfigure(1, weight=2)
        self.image_info_frame.pack(fill='both')

        # Load the clicked image
        img = Image.open(image_name)
        #img = img.resize((300, 300))  # Adjust the size as needed
        img.thumbnail((400, 400))
        photo = ImageTk.PhotoImage(img)

        # Create a label to display the image
        image_label = tk.Label(self.image_info_frame, image=photo)
        image_label.image = photo
        image_label.grid(row=0, column=0, padx=0, pady=0, sticky='nesw')

        # Create a label to display the image name
        info_text_label = tk.Text(self.image_info_frame)
        info_text_label.insert(tk.END, get_tags(image_name))
        info_text_label.grid(row=0, column=1, padx=0, pady=0, sticky='nesw')


SDSearchEngine(input_dir)