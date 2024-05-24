import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import json

class Calculator(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("烘焙成本计算器")
        self.geometry("600x600")

        # 加载配方和价格表
        self.load_recipes()
        self.load_prices()

        # 创建GUI
        self.create_widgets()

    def load_recipes(self):
        try:
            with open('recipes.json', 'r', encoding='utf-8') as file:
                self.recipes = json.load(file)
        except Exception as e:
            messagebox.showerror("加载错误", f"无法加载配方数据: {e}")
            self.recipes = {}

    def load_prices(self):
        try:
            with open('prices.json', 'r', encoding='utf-8') as file:
                self.prices = json.load(file)
        except Exception as e:
            messagebox.showerror("加载错误", f"无法加载价格数据: {e}")
            self.prices = {}

    def create_widgets(self):
        input_frame = ttk.Frame(self)
        input_frame.pack(pady=10)
        self.input_frame = input_frame  # store reference to input_frame

        self.product_entries = {}
        for i, (product, ingredients) in enumerate(self.recipes.items()):
            label = ttk.Label(input_frame, text=product)
            label.grid(row=i, column=0, padx=5, pady=5, sticky="e")  # 使用sticky参数来设置对齐方式

            entry = ttk.Entry(input_frame)
            entry.grid(row=i, column=1, padx=5, pady=5)
            entry.insert(0, "0")
            self.product_entries[product] = entry

        calculate_button = ttk.Button(self, text="计算材料和成本", command=self.calculate_materials)
        calculate_button.pack(pady=10)

        add_product_button = ttk.Button(self, text="添加新品", command=self.add_product)
        add_product_button.pack(pady=10)

        self.output_text = tk.Text(self, height=10, width=80)
        self.output_text.pack(pady=10)

    def calculate_materials(self):
        total_materials = {}
        
        #加上包装与水电煤的大概价格
        total_cost = 1.7

        for product, entry in self.product_entries.items():
            try:
                quantity = int(entry.get())
                if quantity > 0:
                    recipe = self.recipes[product]
                    for ingredient, data in recipe.items():
                        amount = data["amount"] * quantity
                        if ingredient in self.prices:
                            price_info = self.prices[ingredient]
                            price_per_unit = price_info["price"] / price_info["amount"]
                            cost = price_per_unit * amount
                        else:
                            messagebox.showerror("价格错误", f"没有找到{ingredient}的价格信息")
                            continue

                        total_cost += cost

                        if ingredient in total_materials:
                            total_materials[ingredient]["amount"] += amount
                        else:
                            total_materials[ingredient] = {"amount": amount}
            except ValueError:
                messagebox.showerror("输入错误", f"请输入有效的数量为 {product}")

        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, "需要材料和成本：\n")
        for ingredient, data in total_materials.items():
            amount = data["amount"]
            self.output_text.insert(tk.END, f"{ingredient}: {amount} 克\n")
        self.output_text.insert(tk.END, f"\n总成本(含$1.7包装/水电费): ${total_cost:.2f} \n")

    def add_product(self):
        new_product = simpledialog.askstring("添加新品", "请输入新产品的名称:")
        if new_product:
            self.recipes[new_product] = {}  # 初始化新产品的配方为空

            new_recipe = {}  # 新产品的配方
            while True:
                ingredient = simpledialog.askstring("添加原材料", f"请输入{new_product}的原材料名称(输入'完成'退出):")
                if ingredient.lower() == "完成":
                    break
                amount = simpledialog.askfloat("添加原材料", f"请输入{ingredient}的数量:")
                new_recipe[ingredient] = {"amount": amount, "unit": "克"}

            self.recipes[new_product] = new_recipe

            # 更新界面
            i = len(self.product_entries)  # 获取新产品应该在的行索引
            new_label = ttk.Label(self.input_frame, text=new_product)
            new_label.grid(row=i, column=0, padx=5, pady=5, sticky="e")  # 使用sticky参数来设置对齐方式

            self.product_entries[new_product] = ttk.Entry(self.input_frame)
            self.product_entries[new_product].grid(row=i, column=1, padx=5, pady=5)

            # 将新配方写入 JSON 文件
            with open('recipes.json', 'w', encoding='utf-8') as file:
                json.dump(self.recipes, file, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    app = Calculator()
    app.mainloop()
