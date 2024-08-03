import tkinter as tk  
from tkinter import filedialog, messagebox  
from PIL import Image, ImageTk, ImageDraw  
import os  

class SpriteSheetPreview:  
    def __init__(self, root):  
        self.root = root  
        self.root.title("Sprite Sheet Preview") 
  
        self.image = None  
        self.sprites = []  
        self.scale = 1.0  

        # Load image button  
        self.load_button = tk.Button(root, text="加载图像", command=self.load_image)  
        self.load_button.pack()  

        # Delete image button  
        self.delete_button = tk.Button(root, text="删除图像", command=self.delete_image)  
        self.delete_button.pack()  

        # Row and column input  
        self.m_label = tk.Label(root, text="行数 (M):")  
        self.m_label.pack()  
        self.m_entry = tk.Entry(root)  
        self.m_entry.pack()  

        self.n_label = tk.Label(root, text="列数 (N):")  
        self.n_label.pack()  
        self.n_entry = tk.Entry(root)  
        self.n_entry.pack()  

        # Scale buttons  
        self.button_frame = tk.Frame(root)  
        self.button_frame.pack()  

        self.zoom_in_button = tk.Button(self.button_frame, text="放大", command=self.zoom_in)  
        self.zoom_in_button.pack(side=tk.LEFT)  

        self.zoom_out_button = tk.Button(self.button_frame, text="缩小", command=self.zoom_out)  
        self.zoom_out_button.pack(side=tk.LEFT)  

        self.preview_button = tk.Button(self.button_frame, text="预览", command=self.preview_sprites)  
        self.preview_button.pack(side=tk.LEFT)  

        self.gif_button = tk.Button(self.button_frame, text="生成GIF", command=self.save_gif)  
        self.gif_button.pack(side=tk.LEFT)  

        # Canvas for displaying sprites  
        self.canvas = tk.Canvas(root, width=800, height=600)  
        self.canvas.pack()  
        
        self.index = 0  
        self.dragging = False  
        self.start_x = 0  
        self.start_y = 0  

        self.canvas.bind("<ButtonPress-1>", self.start_drag)  
        self.canvas.bind("<B1-Motion>", self.drag)  

    def load_image(self):  
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif;")])  
        if not file_path:  
            return    
        # 增加像素限制  
        Image.MAX_IMAGE_PIXELS = 500_000_000  
      
        self.image = Image.open(file_path).convert("RGBA")  # 确保图像为RGBA模式

        # 可选择缩放图像（例如，将较大图像缩放到最大宽度为2000像素）  
        max_width = 80000  
        if self.image.width > max_width:  
            ratio = max_width / self.image.width  
            new_height = int(self.image.height * ratio)  
            self.image = self.image.resize((max_width, new_height), Image.ANTIALIAS) 

        self.image = self.crop_image(self.image)  # 裁剪透明/白色背景  
        self.image = self.image.resize((self.image.width // 2, self.image.height // 2), Image.LANCZOS)  # 降低分辨率  
        self.sprites = []  
        self.index = 0  
        self.scale = 1.0  
        self.display_image(self.image)  

    def crop_image(self, image):  
            # 获取图像的边界框  
            bbox = image.getbbox()  
            if bbox:  
                # 使用边界框裁剪图像，去掉透明或白色背景  
                return image.crop(bbox)  
            return image  # 如果无边界框，返回原图像  

    def display_image(self, image):  
        self.canvas.delete("all")  
        width = int(image.width * self.scale)  
        height = int(image.height * self.scale)  
        resized_image = image.resize((width, height), Image.LANCZOS)  
        img_tk = ImageTk.PhotoImage(resized_image)  
        self.canvas.create_image(0, 0, anchor=tk.NW, image=img_tk)  
        self.canvas.image = img_tk  
    
    def is_solid_color(self, sprite):  
        # 首先转为 RGBA 模式  
        sprite = sprite.convert("RGBA")  
        data = sprite.getdata()  
        
        total_pixels = len(data)  
        solid_color_count = 0  
        
        for pixel in data:  
            # 判定纯色或透明的条件  
            if pixel[3] == 0 or (pixel[0] == pixel[1] == pixel[2]):  
                solid_color_count += 1  

        # 如果纯色或透明的像素占比超过 70%，则返回 True  
        return solid_color_count / total_pixels > 0.7  

    def zoom_in(self):  
        self.scale *= 1.1  
        if self.image:  
            self.display_image(self.image)  

    def zoom_out(self):  
        self.scale *= 0.9  
        if self.image:  
            self.display_image(self.image)  

    def preview_sprites(self):  
        if self.image is None:  
            messagebox.showwarning("警告", "请先选择一张图像！")  
            return  
        
        try:  
            m = int(self.m_entry.get()) if self.m_entry.get() else 1  # 默认M为1  
            n = int(self.n_entry.get())  
        except ValueError:  
            messagebox.showwarning("警告", "请输入有效的行数和列数！")  
            return  

        img_width, img_height = self.image.size  
        sprite_width = img_width // n  
        sprite_height = img_height // m  

        self.sprites = []  # 清空已有的精灵
        for i in range(m):  
            for j in range(n):  
                box = (j * sprite_width, i * sprite_height, (j + 1) * sprite_width, (i + 1) * sprite_height)  
                sprite = self.image.crop(box)  
                if not self.is_solid_color(sprite):  
                    self.sprites.append(sprite)  

        self.index = 0  
        self.play_sprites()  

    def play_sprites(self):  
        if not self.sprites:  
            messagebox.showinfo("信息", "没有可播放的精灵！")  
            return  
        
        sprite = self.sprites[self.index]  
        self.display_image(sprite)  
        self.index = (self.index + 1) % len(self.sprites)  # 循环播放
        self.root.after(50, self.play_sprites)   # 每50毫秒播放下一个精灵

    def delete_image(self):  
        self.image = None  
        self.sprites = []  
        self.canvas.delete("all")  

    def save_gif(self):  
        if not self.sprites:  
            messagebox.showwarning("警告", "没有可生成的GIF图像！")  
            return  

        file_path = filedialog.asksaveasfilename(defaultextension=".gif", filetypes=[("GIF files", "*.gif")])  
        if not file_path:  
            return  
        
        self.sprites[0].save(  
            file_path,  
            save_all=True,  
            append_images=self.sprites[1:],  
            duration=100,  
            loop=0  
        )  
        messagebox.showinfo("信息", "GIF图像已保存！")  

    def start_drag(self, event):  
        self.dragging = True  
        self.start_x = event.x  
        self.start_y = event.y  

    def drag(self, event):  
        if self.dragging and self.image:  
            dx, dy = event.x - self.start_x, event.y - self.start_y  
            self.canvas.move("all", dx, dy)  
            self.start_x = event.x  
            self.start_y = event.y  

    def stop_drag(self, event):  
        self.dragging = False  

if __name__ == "__main__":  
    root = tk.Tk()  
    app = SpriteSheetPreview(root)  
    root.mainloop()