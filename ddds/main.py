import tkinter as tk
from tkinter import ttk
import platform
import psutil
import socket
import subprocess


def get_cpu_name():
    if platform.system() == "Windows":
        try:
            result = subprocess.check_output(
                "wmic cpu get name",
                shell=True
            ).decode(errors="ignore").splitlines()
            return next(x.strip() for x in result if x.strip() and "Name" not in x)
        except:
            pass
    return platform.processor() or "Неизвестно"


def get_gpu():
    if platform.system() == "Windows":
        try:
            result = subprocess.check_output(
                "powershell -NoProfile -Command \"Get-CimInstance Win32_VideoController | Select-Object -ExpandProperty Name\"",
                shell=True
            ).decode(errors="ignore")
            return result.strip() or "Неизвестно"
        except:
            return "Не удалось определить"
    return "Недоступно"


def gb(value):
    return round(value / (1024 ** 3), 2)


class PCInfo:

    def __init__(self, root):
        self.root = root
        self.root.title("PC INFO")
        self.root.geometry("750x550")
        self.root.configure(bg="#101827")

        title = tk.Label(
            root,
            text="PC INFO",
            font=("Arial", 25, "bold"),
            fg="#60a5fa",
            bg="#101827"
        )
        title.pack(pady=15)

        self.tabs = ttk.Notebook(root)
        self.tabs.pack(fill="both", expand=True, padx=15, pady=10)

        self.frames = {}

        for name in [
            "Процессор",
            "Оперативная память",
            "Видеокарта",
            "Диски",
            "Система",
            "Сеть"
        ]:
            frame = tk.Frame(self.tabs, bg="#172337")
            self.tabs.add(frame, text=name)
            self.frames[name] = frame

        self.refresh_button = tk.Button(
            root,
            text="⟳ Обновить информацию",
            command=self.update_info,
            bg="#2563eb",
            fg="white",
            font=("Arial", 11, "bold"),
            relief="flat",
            padx=15,
            pady=8
        )
        self.refresh_button.pack(pady=10)

        self.update_info()

    def show_info(self, tab, data):
        frame = self.frames[tab]

        for widget in frame.winfo_children():
            widget.destroy()

        for title, value in data:
            row = tk.Frame(frame, bg="#172337")
            row.pack(fill="x", padx=20, pady=9)

            tk.Label(
                row,
                text=title,
                font=("Arial", 10, "bold"),
                fg="#60a5fa",
                bg="#172337",
                width=23,
                anchor="w"
            ).pack(side="left")

            tk.Label(
                row,
                text=str(value),
                font=("Arial", 10),
                fg="white",
                bg="#172337",
                anchor="w",
                justify="left",
                wraplength=420
            ).pack(side="left")

    def update_info(self):

        # CPU
        cpu = [
            ("Модель", get_cpu_name()),
            ("Физические ядра", psutil.cpu_count(logical=False)),
            ("Потоки", psutil.cpu_count(logical=True)),
            ("Загрузка", f"{psutil.cpu_percent(interval=0.5)}%"),
        ]

        freq = psutil.cpu_freq()
        cpu.append((
            "Частота",
            f"{freq.current:.0f} MHz" if freq else "Нет данных"
        ))

        self.show_info("Процессор", cpu)

        # RAM
        ram = psutil.virtual_memory()

        self.show_info("Оперативная память", [
            ("Всего", f"{gb(ram.total)} GB"),
            ("Используется", f"{gb(ram.used)} GB"),
            ("Свободно", f"{gb(ram.available)} GB"),
            ("Загрузка", f"{ram.percent}%")
        ])

        # GPU
        self.show_info("Видеокарта", [
            ("Графический адаптер", get_gpu())
        ])

        # DISKS
        disks = []

        for disk in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(disk.mountpoint)

                disks.append((
                    disk.device,
                    f"Всего: {gb(usage.total)} GB | "
                    f"Свободно: {gb(usage.free)} GB | "
                    f"Занято: {usage.percent}%"
                ))
            except:
                pass

        self.show_info("Диски", disks)

        # SYSTEM
        self.show_info("Система", [
            ("ОС", platform.system()),
            ("Версия", platform.version()),
            ("Имя ПК", platform.node()),
            ("Архитектура", platform.machine()),
            ("Python", platform.python_version())
        ])

        # NETWORK
        addresses = []

        for interface, entries in psutil.net_if_addrs().items():
            for entry in entries:
                if entry.family == socket.AF_INET:
                    addresses.append((
                        interface,
                        entry.address
                    ))

        self.show_info("Сеть", addresses or [
            ("IP", "Не найден")
        ])


if __name__ == "__main__":
    root = tk.Tk()
    app = PCInfo(root)
    root.mainloop()