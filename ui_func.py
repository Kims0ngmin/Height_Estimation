import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import math
import csv
from datetime import datetime
from tkinter import scrolledtext
import matplotlib.colors as mcolors

class ImageEditor:
    def __init__(self, root, image_path):
        self.color_dict = {'x': 'blue', 'y': 'green', 'z': 'orange', 'r': 'yellow', 'h': 'red', 'm': 'white'}
        self.r_line = 0
        self.m_line = 0
        self.real_len = 0
        self.mouse_x = 0
        self.mouse_y = 0
        self.root = root
        self.root.title("Image Editor")

        self.image_path = image_path
        self.image = cv2.imread(image_path)
        self.image = cv2.resize(self.image, (640, 480))
        self.image_copies = [self.image.copy()]
        self.display_image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
        self.photo = ImageTk.PhotoImage(image=Image.fromarray(self.display_image))

        # Create frame
        self.frame = tk.Frame(root)
        self.frame.pack()

        # Creating and Placing canvas
        self.canvas = tk.Canvas(self.frame, width=self.image.shape[1], height=self.image.shape[0])
        self.canvas.pack(side=tk.LEFT)

        # Add Image
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
                
        # Creat output text box
        self.output_text = scrolledtext.ScrolledText(self.frame, width=40, height=30, bg="lightgrey", font=("Helvetica", 10), wrap=tk.WORD)
        self.output_text.pack(side=tk.BOTTOM, anchor="center", fill="y")
        
        # Create a label for displaying mini image
        self.mini_image_label = tk.Label(self.frame)
        self.mini_image_label.pack(side=tk.BOTTOM, anchor="center", padx=10)

        # Display the mini image
        self.display_mini_image()
        
        # Add Button
        self.pick_x_button = tk.Button(self.frame, text="X - axis", command=lambda: self.pick_points('x'), fg="blue")
        self.pick_x_button.pack(side=tk.LEFT, anchor="nw")

        self.pick_y_button = tk.Button(self.frame, text="Y - axis", command=lambda: self.pick_points('y'), fg="green")
        self.pick_y_button.pack(side=tk.LEFT, anchor="nw")

        self.pick_z_button = tk.Button(self.frame, text="Z - axis", command=lambda: self.pick_points('z'), fg="orange")
        self.pick_z_button.pack(side=tk.LEFT, anchor="nw")
        
        self.pick_r_button = tk.Button(self.frame, text="Reference", command=lambda: [self.pick_points('r'), self.get_()], fg="yellow")
        self.pick_r_button.pack(side=tk.LEFT, anchor="nw")
        self.pick_h_button = tk.Button(self.frame, text="Helper", command=lambda: self.pick_points('h'), fg="red")
        self.pick_h_button.pack(side=tk.LEFT, anchor="nw")
        self.pick_m_button = tk.Button(self.frame, text="Measure", command=lambda: self.pick_points('m'), fg="white")
        self.pick_m_button.pack(side=tk.LEFT, anchor="nw")
        
        self.store_button = tk.Button(root, text="Store", command=self.store_data)
        self.store_button.pack(side=tk.RIGHT, anchor="n")
        self.clear_button = tk.Button(root, text="Clear", command=self.clear_lines)
        self.clear_button.pack(side=tk.RIGHT, padx=1)
        self.calculate_button = tk.Button(self.frame, text="Calculate", command=self.cal_height, fg="purple")
        self.calculate_button.pack(side=tk.LEFT, anchor="nw")

        # Points for 'x~m' group
        self.x_points = []  
        self.y_points = [] 
        self.z_points = []  
        self.r_points = []
        self.h_points = []         
        self.m_points = []  

        self.x_lines = [] 
        self.y_lines = [] 
        self.z_lines = []
        self.r_lines = [] 
        self.h_lines = [] 
        self.m_lines = []
        
        self.current_group = None

        self.csv_filename = "lines_data.csv"  # CSV file to store line coordinates

        self.points = []
        self.canvas.bind("<Motion>", self.display_mouse_position)
        

    def display_mouse_position(self, event):
        self.mouse_x = event.x
        self.mouse_y = event.y

        # 마우스 위치가 변경될 때마다 미니 이미지 업데이트
        self.display_mini_image()


    def pick_points(self, group):
        self.current_group = group
        self.points = []  # Reset points when a new group is selected
        self.canvas.bind("<Button-1>", self.get_point)
        self.canvas.bind("<Motion>", self.display_mouse_position)


    def get_point(self, event):
        x, y = event.x, event.y
        self.points.append((x, y))

        # Draw a small circle at the picked point with group-specific color
        point_color= self.color_dict.get(self.current_group)
        rgb_color = mcolors.to_rgb(point_color)
        point_color = (int(rgb_color[2] * 255), int(rgb_color[1] * 255), int(rgb_color[0] * 255))

        cv2.circle(self.image, (x, y), 3, point_color, -1)
        getattr(self, f"{self.current_group}_points").append((x, y))
        
        # Display coordinates in the output text box
        if len(self.points) == 1:
            self.output_text.insert(tk.END, f"<< {self.current_group}_Line >>\n")
            self.output_text.insert(tk.END, f"Start Point : ({x}, {y})\n")

        if len(self.points) == 2:
            # Draw a line between the two points with group-specific color
            line_color = self.color_dict.get(self.current_group)
            rgb_color = mcolors.to_rgb(line_color)
            line_color = (int(rgb_color[2] * 255), int(rgb_color[1] * 255), int(rgb_color[0] * 255))
            cv2.line(self.image, self.points[0], self.points[1], line_color, 2)
            # calculate pixel line distance
            distance_pixels = round(math.sqrt((self.points[1][0] - self.points[0][0])**2 + (self.points[1][1] - self.points[0][1])**2), 2)
            
            # Store the line coordinates for the current group
            getattr(self, f"{self.current_group}_lines").append(self.points)
            self.points = []
            self.image_copies.append(self.image.copy())
            
            # Display coordinates in the output text box
            self.output_text.insert(tk.END, f"End Point : ({x}, {y})\n")
            self.output_text.insert(tk.END, f"Line distance : {distance_pixels}\n\n")
                        
            # Save Data for Length (= Pixel Length on Frame) Measurement
            if self.current_group=='r':
                self.r_line = distance_pixels
            if self.current_group=='m':
                self.m_line = distance_pixels
                
            # Reset points after drawing a line
            self.points = []

        # Update the displayed image
        self.display_image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
        self.photo = ImageTk.PhotoImage(image=Image.fromarray(self.display_image))
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
        
    def get_input(self,entry):
        real_length = entry.get()

        # Update the class variable or perform any desired action with the input
        self.real_len = float(real_length)

        # Close the input window
        self.output_text.insert(tk.END, f"Input real length : {self.real_len}")
        entry.master.destroy()
        
    def get_(self):
        # button to hand over the reference length entered in the output text box
        input_window = tk.Toplevel(self.root)
        input_window.title("Get Input")

        # Add labels and an entry widget for input
        label = tk.Label(input_window, text="Input real length:")
        label.pack(pady=10)

        entry = tk.Entry(input_window)
        entry.pack(pady=10)

        get_input_button = tk.Button(input_window, text="Get Input", command=lambda: self.get_input(entry))
        get_input_button.pack(pady=10)

    def norm(self, point1, point2):
        xdiff = point1[0] - point2[0]
        ydiff = point1[1] - point2[1]

        norm = math.sqrt(xdiff * xdiff + ydiff * ydiff)
        return norm

    def cal_height(self):
        # Extract X, Y, and Z lines
        x_lines = getattr(self, "x_lines")
        y_lines = getattr(self, "y_lines")
        z_lines = getattr(self, "z_lines")
        r_lines = getattr(self, "r_lines")
        m_lines = getattr(self, "m_lines")
        length = getattr(self, "real_len" )

        # Calculate intersection points
        x_intersection = self.calculate_intersection(x_lines)
        y_intersection = self.calculate_intersection(y_lines)
        z_intersection = self.calculate_intersection(z_lines)

        # Draw markers at the intersection points
        self.draw_marker(x_intersection, (0,255,0))
        self.draw_marker(y_intersection, (0,255,0))
        self.draw_marker(z_intersection, (0,255,0))

        # Optionally, display the coordinates in the output text box
        self.output_text.insert(tk.END, "Intersection Point (X): {}\n".format(x_intersection))
        self.output_text.insert(tk.END, "Intersection Point (Y): {}\n".format(y_intersection))
        self.output_text.insert(tk.END, "Intersection Point (Z): {}\n".format(z_intersection))
    
        intersection_line = None
        if x_intersection and y_intersection:
            intersection_line = (x_intersection, y_intersection)
            #cv2.line(self.image, x_intersection, y_intersection, (255, 0, 255), 2)
            self.update_displayed_image()

       
        rb = r_lines[0][0]
        rt = r_lines[0][1]
        mb = m_lines[0][0]
        mt = m_lines[0][1]


        if rt[1]>rb[1]:
            x = rb
            rb = rt
            rt = x
        
        if mt[1]>mb[1]:
            x = mb
            mb = mt
            mt = x

        print(rb)
        b_line = (rb,mb)
        
        ver_line = []
        ver_line.append(intersection_line)
        ver_line.append(b_line)


        vertex = self.calculate_intersection(ver_line)
        self.draw_marker(vertex, (255,255,0))
        
        
        ver_line = []
        ver_rt = (vertex,rt)
        ver_line.append(ver_rt)
        ver_line.append((mb,mt))

        t = self.calculate_intersection(ver_line)


        self.output_text.insert(tk.END, "Intersection Point (VERTEX): {}\n".format(vertex))
        self.output_text.insert(tk.END, "Intersection Point (t): {}\n".format(t))
        
        self.draw_marker(t, (0,0,0))

        measure = ((self.norm(mt,mb) / self.norm(t,mb)) * (self.norm(z_intersection,t) / self.norm(z_intersection,mt)) * length)
        self.output_text.insert(tk.END, "measure: {}\n".format(measure))
        

    def calculate_intersection(self, lines):
        # Calculate intersection point for a pair of lines
        if len(lines) >= 2:
            line1 = lines[-2]
            line2 = lines[-1]

            x1, y1 = line1[0]
            x2, y2 = line1[1]

            x3, y3 = line2[0]
            x4, y4 = line2[1]

            denominator = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
            
            if denominator != 0:
                intersection_x = ((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)) / denominator
                intersection_y = ((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)) / denominator

                return int(intersection_x), int(intersection_y)
            
        return None

    def draw_marker(self, intersection_point, color):
        # Draw a marker or line at the calculated intersection point
        if intersection_point:
            self.update_displayed_image()

            
        
    def store_data(self):
        image_name = self.image_path.split('/')[-1]  # Get the image file name
        
        with open(self.csv_filename, mode='a', newline='') as file:
            writer = csv.writer(file)
            today = datetime.today().strftime("\n<< %Y/%m/%d %H:%M:%S >>")
            writer.writerow([today])

        # Iterate over all groups ('x', 'y', 'z', 'r', 'h', 'm') and store the corresponding lines
        for group in ['x', 'y', 'z', 'r', 'h', 'm']:
            group_points = getattr(self, f"{group}_points")

            with open(self.csv_filename, mode='a', newline='') as file:
                writer = csv.writer(file)
                for i in range(0, len(group_points), 2):
                    x1, y1 = group_points[i]
                    x2, y2 = group_points[i + 1]
                    writer.writerow([image_name, group, x1, y1, x2, y2])
                    
        print("!!Save successfully!!")
        
    def clear_lines(self):
        if self.current_group is not None:
            # Remove the last line for the currently selected group
            group_lines = getattr(self, f"{self.current_group}_lines")
            if group_lines:
                group_lines.pop()

            # Remove the last two points for the currently selected group
            group_points = getattr(self, f"{self.current_group}_points")
            if len(group_points) >= 2:
                group_points.pop()
                group_points.pop()

            self.image = cv2.imread(self.image_path)
            self.image = cv2.resize(self.image, (640, 480))
            self.update_displayed_image()
            
    def update_displayed_image(self):
            for group in ['x', 'y', 'z', 'r', 'h', 'm']:
                group_points = getattr(self, f"{group}_points")
                group_lines = getattr(self, f"{group}_lines")
                line_color = self.color_dict.get(group)
                rgb_color = mcolors.to_rgb(line_color)
                line_color = (int(rgb_color[2] * 255), int(rgb_color[1] * 255), int(rgb_color[0] * 255))

                # Redraw all points for the current group
                for point in group_points:
                    x, y = point
                    cv2.circle(self.image, (x, y), 3, line_color, -1)

                # Redraw all lines for the current group
                for line in group_lines:
                    x1, y1 = line[0]
                    x2, y2 = line[1]
                    cv2.line(self.image, (x1, y1), (x2, y2), line_color, 2)

            self.display_image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
            self.photo = ImageTk.PhotoImage(image=Image.fromarray(self.display_image))
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
            # Call the method to update the mini image
            self.display_mini_image()
            
    def display_mini_image(self):
        # Set area size based on center
        region_size = 100
        
        image_height, image_width = self.image.shape[:2]

        # Calculate the desired size of the area at the mouse location
        top_left_x = self.mouse_x - 50
        top_left_y = self.mouse_y - 50
        bottom_right_x = self.mouse_x + 50
        bottom_right_y = self.mouse_y + 50

        # Create a full area of black background first
        image_zoom = np.zeros((region_size, region_size, 3), dtype=np.uint8)

        # Calculate where to insert the actual image
        insert_x1 = max(0, -top_left_x)
        insert_y1 = max(0, -top_left_y)
        insert_x2 = region_size - max(0, bottom_right_x - image_width)
        insert_y2 = region_size - max(0, bottom_right_y - image_height)

        # Calculate the coordinates to import from the source image
        src_x1 = max(0, top_left_x)
        src_y1 = max(0, top_left_y)
        src_x2 = min(image_width, bottom_right_x)
        src_y2 = min(image_height, bottom_right_y)

        # Cut the area from the image and insert it into the black background
        image_zoom[insert_y1:insert_y2, insert_x1:insert_x2] = self.image[src_y1:src_y2, src_x1:src_x2]

        mini_photo = cv2.resize(image_zoom, (200, 200))

        mini_photo = cv2.cvtColor(mini_photo, cv2.COLOR_BGR2RGB)
        cv2.circle(mini_photo, (100, 100), 7, (255, 255, 255), 2)
        mini_photo = ImageTk.PhotoImage(image=Image.fromarray(mini_photo))

        self.mini_image_label.config(image=mini_photo)
        self.mini_image_label.image = mini_photo