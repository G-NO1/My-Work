import customtkinter as ctk
from tkinter import messagebox
import json

# 高分屏适配
try:
    from ctypes import windll

    windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

# ============ 国企经典配色方案 ============
COLORS = {
    # 主色调 - 国企经典红色系
    "primary": "#B22222",  # 国企经典深红色
    "primary_hover": "#8B0000",  # 更深红色悬停
    "primary_light": "#FFE4E1",  # 淡红色

    # 功能色 - 国企传统配色
    "success": "#228B22",  # 森林绿（成功）
    "warning": "#DAA520",  # 金菊色（警告/清空）
    "danger": "#B22222",   # 深红色（危险/删除）
    "info": "#4682B4",    # 钢蓝色（信息）

    # 背景色 - 稳重商务
    "bg_light": "#F5F5F5",  # 浅灰白背景
    "bg_dark": "#2F4F4F",  # 深岩灰背景
    "card_light": "#FFFFFF",  # 白色卡片
    "card_dark": "#3D3D3D",  # 深灰卡片
    "section_light": "#E8E8E8",  # 浅灰区域
    "section_dark": "#4A4A4A",  # 中灰区域

    # 文字色
    "text_primary_light": "#333333",  # 深灰（接近黑色）
    "text_primary_dark": "#F0F0F0",  # 接近白色
    "text_secondary_light": "#666666",  # 中灰色
    "text_secondary_dark": "#A0A0A0",  # 浅灰色

    # 边框色 - 传统风格
    "border_light": "#C0C0C0",  # 经典灰色
    "border_dark": "#696969",   # 深灰色

    # SegmentedButton 文字颜色
    "segmented_text_selected_light": "#FFFFFF",
    "segmented_text_selected_dark": "#FFFFFF",
    "segmented_text_unselected_light": "#333333",
    "segmented_text_unselected_dark": "#D0D0D0",
}

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

BASE_URL = "https://gwplus.chememall.com/emallplus-gateway"
ENDPOINT = "/plansale/p/maintenance/plan/updateInfo"
FULL_URL = BASE_URL + ENDPOINT

FIELDS = [
    ("生产企业", "manufacturerCode"), ("工厂", "factoryCode"), ("分销渠道", "distributionChannelCode"),
    ("部门", "departmentCode"), ("客户组", "buyerGroupId"), ("量", "quantity"), ("下发 SAP", "needSap")
]


class PlanCard(ctk.CTkFrame):
    def __init__(self, parent, remove_callback):
        super().__init__(parent)
        self.remove_callback = remove_callback
        self.is_collapsed = False

        # 现代卡片样式
        self.configure(
            fg_color=(COLORS["card_light"], COLORS["card_dark"]),
            corner_radius=16,
            border_width=1,
            border_color=(COLORS["border_light"], COLORS["border_dark"])
        )
        self.pack(fill="x", padx=20, pady=12)

        # === 顶层控制栏 ===
        self.top_bar = ctk.CTkFrame(self, fg_color="transparent")
        self.top_bar.pack(fill="x", padx=15, pady=12)

        # 折叠按钮 - 圆润风格
        self.btn_toggle = ctk.CTkButton(
            self.top_bar,
            text="▼",
            width=36,
            height=36,
            corner_radius=18,
            fg_color=(COLORS["section_light"], COLORS["section_dark"]),
            hover_color=(COLORS["border_light"], COLORS["border_dark"]),
            text_color=(COLORS["text_primary_light"], COLORS["text_primary_dark"]),
            font=("Arial", 13, "bold"),
            command=self.toggle_collapse
        )
        self.btn_toggle.pack(side="left", padx=(0, 12))

        # 模式标签 - 清晰的高对比度徽章风格
        self.mode_badge = ctk.CTkFrame(
            self.top_bar,
            fg_color=(COLORS["primary"], COLORS["primary"]),
            corner_radius=8,
            height=32,
            border_width=1,
            border_color=(COLORS["primary_hover"], COLORS["primary_hover"])
        )
        self.mode_badge.pack(side="left", padx=(0, 12))
        self.mode_label = ctk.CTkLabel(
            self.mode_badge,
            text="数据更新",
            font=("Microsoft YaHei UI", 12, "bold"),
            text_color=("white", "white")
        )
        self.mode_label.pack(padx=14, pady=5)

        # 编码显示 - 使用更醒目的样式
        self.summary_label = ctk.CTkLabel(
            self.top_bar,
            text="未命名计划",
            font=("Microsoft YaHei UI", 14, "bold"),
            text_color=(COLORS["text_primary_light"], COLORS["text_primary_dark"])
        )
        self.summary_label.pack(side="left", padx=8)

        # 移除按钮 - 圆形危险按钮
        self.btn_del = ctk.CTkButton(
            self.top_bar,
            text="✕",
            width=36,
            height=36,
            corner_radius=18,
            fg_color="transparent",
            hover_color=(COLORS["danger"], COLORS["danger"]),
            text_color=COLORS["danger"],
            font=("Arial", 16, "bold"),
            border_width=1,
            border_color=(COLORS["border_light"], COLORS["danger"]),
            command=lambda: self.remove_callback(self)
        )
        self.btn_del.pack(side="right", padx=0)

        # === 可折叠内容区域 ===
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(fill="x", padx=15, pady=(0, 12))

        # 模式选择区域
        mode_section = ctk.CTkFrame(
            self.content_frame,
            fg_color=(COLORS["section_light"], COLORS["section_dark"]),
            corner_radius=12
        )
        mode_section.pack(fill="x", pady=(0, 12))
        self.op_mode = ctk.CTkSegmentedButton(
            mode_section,
            values=["数据更新", "清空字段", "逻辑删除"],
            command=self.on_mode_change,
            height=48,
            font=("Microsoft YaHei UI", 14, "bold"),
            fg_color=(COLORS["bg_light"], COLORS["bg_dark"]),
            selected_color="#A9A9A9",  # 深灰色选中背景
            selected_hover_color="#808080",  # 灰色悬停
            unselected_color=(COLORS["section_light"], COLORS["section_dark"]),
            unselected_hover_color=(COLORS["border_light"], COLORS["border_dark"]),
            dynamic_resizing=False,
            text_color=(COLORS["segmented_text_unselected_light"], COLORS["segmented_text_unselected_dark"]),
            text_color_disabled=(COLORS["segmented_text_unselected_light"], COLORS["segmented_text_unselected_dark"])
        )
        self.op_mode.set("数据更新")
        self.op_mode.pack(fill="x", padx=10, pady=10)

        # 基础信息区域
        base_section = ctk.CTkFrame(
            self.content_frame,
            fg_color=(COLORS["section_light"], COLORS["section_dark"]),
            corner_radius=12
        )
        base_section.pack(fill="x", pady=(0, 12))

        base_inner = ctk.CTkFrame(base_section, fg_color="transparent")
        base_inner.pack(fill="x", padx=15, pady=12)

        # 左侧：计划编码
        left_box = ctk.CTkFrame(base_inner, fg_color="transparent")
        left_box.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(
            left_box,
            text="计划编码",
            font=("Microsoft YaHei UI", 11, "bold"),
            text_color=(COLORS["text_secondary_light"], COLORS["text_secondary_dark"])
        ).pack(anchor="w", pady=(0, 6))

        self.plan_code = ctk.CTkEntry(
            left_box,
            height=38,
            corner_radius=8,
            placeholder_text="请输入计划编码...",
            font=("Microsoft YaHei UI", 12),
            fg_color=(COLORS["card_light"], COLORS["card_dark"]),
            border_color=(COLORS["border_light"], COLORS["border_dark"])
        )
        self.plan_code.pack(fill="x", pady=(0, 0))
        self.plan_code.bind("<KeyRelease>", self.update_summary)

        # 右侧：周期选择
        right_box = ctk.CTkFrame(base_inner, fg_color="transparent")
        right_box.pack(side="right", padx=(20, 0))

        ctk.CTkLabel(
            right_box,
            text="周期",
            font=("Microsoft YaHei UI", 11, "bold"),
            text_color=(COLORS["text_secondary_light"], COLORS["text_secondary_dark"])
        ).pack(anchor="w", pady=(0, 6))

        self.plan_type = ctk.CTkOptionMenu(
            right_box,
            values=["年计划", "混合计划"],
            width=140,
            height=38,
            corner_radius=4,
            font=("Microsoft YaHei UI", 12),
            fg_color="#D3D3D3",      # 浅灰色背景
            button_color="#A9A9A9",  # 深灰色按钮
            button_hover_color="#808080",  # 灰色悬停
            text_color="black",      # 黑色文字
            dropdown_text_color="black"  # 下拉菜单黑色文字
        )
        self.plan_type.set("年计划")
        self.plan_type.pack()

        # 详细字段区域
        self.body_section = ctk.CTkFrame(
            self.content_frame,
            fg_color=(COLORS["section_light"], COLORS["section_dark"]),
            corner_radius=12
        )
        self.body_section.pack(fill="x")

        self.body_frame = ctk.CTkFrame(self.body_section, fg_color="transparent")
        self.body_frame.pack(fill="x", padx=15, pady=12)
        self.body_frame.grid_columnconfigure((1, 3, 5), weight=1)

        self.field_widgets = {}
        self.create_fields()

    def create_fields(self):
        for i, (label_text, key) in enumerate(FIELDS):
            row, col = i // 3, (i % 3) * 2

            # 标签
            lbl = ctk.CTkLabel(
                self.body_frame,
                text=label_text,
                font=("Microsoft YaHei UI", 11, "bold"),
                text_color=(COLORS["text_secondary_light"], COLORS["text_secondary_dark"]),
                anchor="e"
            )
            lbl.grid(row=row, column=col, padx=(10, 8), pady=10, sticky="e")

            # 输入控件
            if key == "needSap":
                widget = ctk.CTkSwitch(
                    self.body_frame,
                    text="",
                    progress_color=COLORS["success"],
                    button_color=COLORS["success"],
                    button_hover_color=COLORS["success"]
                )
            else:
                widget = ctk.CTkEntry(
                    self.body_frame,
                    height=34,
                    corner_radius=8,
                    font=("Microsoft YaHei UI", 11),
                    fg_color=(COLORS["card_light"], COLORS["card_dark"]),
                    border_color=(COLORS["border_light"], COLORS["border_dark"])
                )
            widget.grid(row=row, column=col + 1, padx=(0, 10), pady=10, sticky="ew")
            self.field_widgets[key] = {"widget": widget, "label": lbl}

    def toggle_collapse(self):
        if self.is_collapsed:
            self.content_frame.pack(fill="x", padx=15, pady=(0, 12))
            self.btn_toggle.configure(text="▼")
            self.is_collapsed = False
        else:
            self.content_frame.pack_forget()
            self.btn_toggle.configure(text="▶")
            self.is_collapsed = True

    def update_summary(self, event=None):
        code = self.plan_code.get().strip()
        self.summary_label.configure(text=code if code else "未命名计划")

    def on_mode_change(self, mode):
        # 更新徽章样式
        if "更新" in mode:
            color = COLORS["primary"]
            bg_color = (COLORS["primary_light"], COLORS["primary"])
            text_color = (COLORS["primary"], "white")
            self.mode_label.configure(text="数据更新")
            self.body_section.pack(fill="x")
            for k in self.field_widgets:
                self.field_widgets[k]["widget"].grid()
                self.field_widgets[k]["label"].grid()
        elif "清空" in mode:
            color = COLORS["warning"]
            bg_color = ("#FEF3C7", COLORS["warning"])
            text_color = (COLORS["warning"], "white")
            self.mode_label.configure(text="清空字段")
            self.body_section.pack(fill="x")
            self.field_widgets["quantity"]["widget"].grid_remove()
            self.field_widgets["quantity"]["label"].grid_remove()
        else:
            color = COLORS["danger"]
            bg_color = ("#FEE2E2", COLORS["danger"])
            text_color = (COLORS["danger"], "white")
            self.mode_label.configure(text="逻辑删除")
            self.body_section.pack_forget()

        self.configure(border_color=(color, color))
        self.mode_badge.configure(fg_color=bg_color)
        self.mode_label.configure(text_color=text_color)

    def get_data(self):
        code = self.plan_code.get().strip()
        if not code: return None
        mode = self.op_mode.get()

        # 将中文周期选择映射回英文值
        plan_type_mapping = {
            "年计划": "year",
            "混合计划": "month"
        }
        selected_plan_type = self.plan_type.get()
        plan_type_english = plan_type_mapping.get(selected_plan_type, "year")

        data = {"planCode": code, "type": plan_type_english}
        if "删除" in mode:
            data.update({"updateType": "remove", "aliveFlag": "0"})
        else:
            data["updateType"] = "remove" if "清空" in mode else "update"
            for key, info in self.field_widgets.items():
                if "清空" in mode and key == "quantity": continue
                w = info["widget"]
                val = w.get() if isinstance(w, ctk.CTkSwitch) else w.get().strip()
                if val != "":
                    if key == "quantity":
                        try:
                            data[key] = float(val)
                        except:
                            pass
                    elif key == "needSap":
                        data[key] = True if val == 1 else False
                    else:
                        data[key] = val
        return data


class ResultWindow(ctk.CTkToplevel):
    def __init__(self, parent, json_str):
        super().__init__(parent)
        self.title("报文生成成功")
        self.geometry("900x750")
        self.after(200, lambda: (self.attributes("-topmost", True), self.focus_force()))

        # 设置背景色
        self.configure(fg_color=(COLORS["bg_light"], COLORS["bg_dark"]))

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # 顶部横幅 - 渐变效果
        banner = ctk.CTkFrame(
            self,
            fg_color=COLORS["primary"],
            height=75,
            corner_radius=0
        )
        banner.grid(row=0, column=0, sticky="ew")

        banner_content = ctk.CTkFrame(banner, fg_color="transparent")
        banner_content.pack(fill="x", padx=25, pady=15)

        ctk.CTkLabel(
            banner_content,
            text="API 端点",
            text_color="white",
            font=("Microsoft YaHei UI", 11, "bold")
        ).pack(anchor="w", pady=(0, 5))

        url_entry = ctk.CTkEntry(
            banner_content,
            height=38,
            font=("Consolas", 11),
            corner_radius=8,
            fg_color=(COLORS["card_light"], COLORS["card_dark"]),
            border_width=0
        )
        url_entry.pack(fill="x")
        url_entry.insert(0, FULL_URL)
        url_entry.configure(state="readonly")

        # JSON 内容区域
        content_frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        content_frame.grid(row=1, column=0, sticky="nsew", padx=25, pady=20)
        content_frame.grid_rowconfigure(0, weight=1)
        content_frame.grid_columnconfigure(0, weight=1)

        # JSON 文本框带标签
        json_section = ctk.CTkFrame(
            content_frame,
            fg_color=(COLORS["section_light"], COLORS["section_dark"]),
            corner_radius=12
        )
        json_section.grid(row=0, column=0, sticky="nsew")
        json_section.grid_rowconfigure(1, weight=1)
        json_section.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            json_section,
            text="请求体 (JSON)",
            font=("Microsoft YaHei UI", 12, "bold"),
            text_color=(COLORS["text_primary_light"], COLORS["text_primary_dark"])
        ).grid(row=0, column=0, sticky="w", padx=15, pady=(12, 8))

        self.txt = ctk.CTkTextbox(
            json_section,
            font=("Consolas", 13),
            corner_radius=0,
            border_width=0,
            fg_color=(COLORS["card_light"], COLORS["card_dark"])
        )
        self.txt.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))
        self.txt.insert("0.0", json_str)

        # 底部操作栏
        footer = ctk.CTkFrame(
            self,
            height=90,
            fg_color="transparent",
            corner_radius=0
        )
        footer.grid(row=2, column=0, sticky="ew", padx=25, pady=(0, 20))

        btn_container = ctk.CTkFrame(footer, fg_color="transparent")
        btn_container.pack(expand=True)

        # 主要操作按钮
        ctk.CTkButton(
            btn_container,
            text="📋 复制全部 (URL + JSON)",
            font=("Microsoft YaHei UI", 13, "bold"),
            height=48,
            width=240,
            corner_radius=10,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            command=lambda: self.copy(f"URL: {FULL_URL}\n\n{json_str}")
        ).pack(side="left", padx=8)

        # 次要操作按钮
        ctk.CTkButton(
            btn_container,
            text="仅复制 JSON",
            font=("Microsoft YaHei UI", 12),
            height=48,
            width=140,
            corner_radius=10,
            fg_color=COLORS["success"],
            hover_color="#059669",
            command=lambda: self.copy(json_str)
        ).pack(side="left", padx=8)

        # 关闭按钮
        ctk.CTkButton(
            btn_container,
            text="关闭",
            font=("Microsoft YaHei UI", 12),
            height=48,
            width=100,
            corner_radius=10,
            fg_color="transparent",
            hover_color=(COLORS["section_light"], COLORS["section_dark"]),
            border_width=1,
            border_color=(COLORS["border_light"], COLORS["border_dark"]),
            text_color=(COLORS["text_secondary_light"], COLORS["text_secondary_dark"]),
            command=self.destroy
        ).pack(side="left", padx=8)

    def copy(self, txt):
        self.clipboard_clear()
        self.clipboard_append(txt)
        self.update()
        messagebox.showinfo("成功", "已复制到剪贴板", parent=self)


class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("EMall 计划维护助手")
        self.geometry("1200x900")

        # 设置主窗口背景
        self.configure(fg_color=(COLORS["bg_light"], COLORS["bg_dark"]))

        # 顶部导航栏 - 现代设计
        self.nav = ctk.CTkFrame(
            self,
            height=85,
            corner_radius=0,
            fg_color=(COLORS["card_light"], COLORS["card_dark"]),
            border_width=0,
            border_color=(COLORS["border_light"], COLORS["border_dark"])
        )
        self.nav.pack(fill="x")

        # 左侧标题
        left_section = ctk.CTkFrame(self.nav, fg_color="transparent")
        left_section.pack(side="left", padx=35, pady=18)

        title_frame = ctk.CTkFrame(left_section, fg_color="transparent")
        title_frame.pack()

        ctk.CTkLabel(
            title_frame,
            text="📦 计划维护助手",
            font=("Microsoft YaHei UI", 22, "bold"),
            text_color=COLORS["primary"]
        ).pack(side="left")

        version_badge = ctk.CTkFrame(
            title_frame,
            fg_color=(COLORS["section_light"], COLORS["section_dark"]),
            corner_radius=10,
            height=26
        )
        # version_badge.pack(side="left", padx=15)
        # ctk.CTkLabel(
        #     version_badge,
        #     text="v5.0",
        #     font=("Microsoft YaHei UI", 10, "bold"),
        #     text_color=(COLORS["text_secondary_light"], COLORS["text_secondary_dark"])
        # ).pack(padx=10, pady=2)

        # 右侧操作按钮组
        right_section = ctk.CTkFrame(self.nav, fg_color="transparent")
        right_section.pack(side="right", padx=35)

        # 清空按钮
        ctk.CTkButton(
            right_section,
            text="清空",
            font=("Microsoft YaHei UI", 12),
            width=80,
            height=40,
            corner_radius=4,
            fg_color="#C0C0C0",      # 经典灰色背景
            hover_color="#A0A0A0",   # 深灰色悬停
            text_color="black",     # 黑色文字
            border_width=1,
            border_color="#808080",
            command=self.clear_all
        ).pack(side="left", padx=8)

        # 新增按钮
        ctk.CTkButton(
            right_section,
            text="新增计划",
            font=("Microsoft YaHei UI", 12),
            width=100,
            height=40,
            corner_radius=4,
            fg_color="#87CEEB",      # 浅天蓝色背景
            hover_color="#5F9EA0",   # 深蓝色悬停
            text_color="black",      # 黑色文字
            border_width=1,
            border_color="#4682B4",
            command=self.add_card
        ).pack(side="left", padx=8)

        # 生成按钮（主操作）
        ctk.CTkButton(
            right_section,
            text="生成报文",
            font=("Microsoft YaHei UI", 12, "bold"),
            width=110,
            height=40,
            corner_radius=4,
            fg_color="#4169E1",      # 皇家蓝背景
            hover_color="#0000CD",   # 中蓝色悬停
            text_color="white",      # 白色文字
            border_width=1,
            border_color="#00008B",
            command=self.generate
        ).pack(side="left", padx=8)

        # 滚动内容区域
        self.scroll = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent"
        )
        self.scroll.pack(fill="both", expand=True, padx=15, pady=20)

        self.cards = []
        self.add_card()

    def add_card(self):
        card = PlanCard(self.scroll, self.remove_card)
        self.cards.append(card)

    def remove_card(self, card):
        card.destroy()
        if card in self.cards:
            self.cards.remove(card)

    def clear_all(self):
        if messagebox.askyesno("确认操作", "确定要清空所有计划吗？", parent=self):
            for c in self.cards:
                c.destroy()
            self.cards.clear()
            self.add_card()

    def generate(self):
        plans = [c.get_data() for c in self.cards if c.get_data()]
        if not plans:
            messagebox.showwarning("提示", "请至少填写一个计划的内容", parent=self)
            return
        ResultWindow(self, json.dumps({"plans": plans}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    app = MainApp()
    app.mainloop()