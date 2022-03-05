from tkinter import *

root = Tk()
root.title('TxtGradeManager')
root.geometry("1200x750+100+25")

# Create Clear Function
def clear():
	my_text.delete(1, END)

# Grab the text from the text box
def get_text():
	my_label.config(text=my_text.get(1.0, 3.0))

my_text = Text(root, width="100", height="30", font=("Courier", 13))
my_text.pack(pady=20)

button_frame = Frame(root)
button_frame.pack()

clear_button = Button(button_frame, text="Añadir estudiante", command=clear)
clear_button.grid(row=0, column=0)

get_text_button = Button(button_frame, text="Añadir evaluación", command=get_text)
get_text_button.grid(row=0, column=1, padx=20)

my_label = Label(root, text='')
my_label.pack(pady=20)



root.mainloop()