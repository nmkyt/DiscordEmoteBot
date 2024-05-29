from tkinter import ttk
import customtkinter as ctk
import bot_controller

ctk.set_appearance_mode('dark')
ctk.set_default_color_theme('dark-blue')

botGUI = ctk.CTk()
botGUI.title("Discord Emote Bot v2.0")

botGUI.geometry("1200x800")

label = ctk.CTkLabel(botGUI, text='Bot console')
label.pack(pady=20)

entry1_frame = ctk.CTkFrame(botGUI)
entry1_frame.pack(padx=10, pady=5, fill='x')
entry1_label = ctk.CTkLabel(entry1_frame, text="Message id:")
entry1_label.pack(side='left', padx=5)
entry1 = ctk.CTkEntry(entry1_frame)
entry1.pack(side='left', padx=5, fill='x', expand=True)

entry2_frame = ctk.CTkFrame(botGUI)
entry2_frame.pack(padx=10, pady=5, fill='x')
entry2_label = ctk.CTkLabel(entry2_frame, text="Duration:")
entry2_label.pack(side='left', padx=5)
entry2 = ctk.CTkEntry(entry2_frame)
entry2.pack(side='left', padx=5, fill='x', expand=True)

submit_button = ctk.CTkButton(botGUI, text="Submit", command=bot_controller.process_input)
submit_button.pack(padx=10, pady=20)

entries_frame = ttk.Frame(botGUI)
entries_frame.pack(pady=10, fill="x")

header_message_id = ttk.Label(entries_frame, text="Message ID")
header_message_id.grid(row=0, column=0, padx=10, pady=5)

header_duration = ttk.Label(entries_frame, text="Duration")
header_duration.grid(row=0, column=1, padx=10, pady=5)

header_checkbox = ttk.Label(entries_frame, text="Option")
header_checkbox.grid(row=0, column=2, padx=10, pady=5)

