import tkinter as tk
from tkinter import filedialog, messagebox
import PyPDF2
import re
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime

def search_pdf(pdf_path, search_term, case_sensitive):
    # Search for a term in the specified file and return lines containing the term.
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        results = []

        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            text = page.extract_text()

            if text:
                # split into lines
                lines = text.split('\n')
                for line in lines:
                    if (case_sensitive and search_term in line) or \
                        (not case_sensitive and re.search(search_term, line, re.IGNORECASE)):
                        results.append((page_num + 1, line.strip()))  #storing page number and line

    return results

def browse_file():
    # Open a file dialog to select a PDF file.
    file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
    if file_path:
        pdf_file_path_var.set(file_path)

def perform_search():
    # Perform the search when the button is clicked.
    pdf_path = pdf_file_path_var.get()
    search_term = search_term_var.get()
    case_sensitive = case_sensitive_var.get()  # state of the case-sensitive checkbox

    if not pdf_path or not search_term:
        messagebox.showwarning("Input Error", "Provide a PDF file and a search term.")
        return

    global found_results  # Declare found_results as global to access in save_report
    found_results = search_pdf(pdf_path, search_term, case_sensitive)

    results_text_widget.delete(1.0, tk.END)  # previous results

    if found_results:
        results_count = len(found_results)  # found results
        results_text = f"Search Results for: '{search_term}'\nTotal Results: {results_count}\n\n"
        for page, line in found_results:
            results_text += f'Found on page {page}:\n{line}\n'
        results_text_widget.insert(tk.END, results_text)

        # Enable the save report button
        save_report_button.config(state=tk.NORMAL)
    else:
        results_text_widget.insert(tk.END, f'No results found for the term: "{search_term}".')
        save_report_button.config(state=tk.DISABLED)  # Disable the save report button

def draw_wrapped_text(canvas, text, x, y, max_width):
    words = text.split(' ')
    current_line = ''
    line_y = y
    height = letter

    for word in words:
        # Check if adding this word exceeds the max width
        test_line = f"{current_line} {word}".strip()
        if canvas.stringWidth(test_line, 'Helvetica', 12) < max_width:
            current_line = test_line
        else:
            # Draw the current line and start a new one
            if current_line:  # Prevent drawing an empty line
                canvas.drawString(x, line_y, current_line)
                line_y -= 15  # Move down for the next line
            current_line = word  # Start a new line with the current word

            # Check if line_y is out of bounds for current page
            if line_y < 50:  # Start a new page if the space is low
                canvas.showPage()
                line_y = height - 50  # Reset to top of new page

    # Draw any remaining text
    if current_line:
        canvas.drawString(x, line_y, current_line)
        line_y -= 15  # Move down for next potential line

    return line_y  # Return the new y position

def save_report():
    if found_results:
        report_path = filedialog.asksaveasfilename(defaultextension=".pdf",
                                                    filetypes=[("PDF files", "*.pdf")],
                                                    title="Save Report As")
        if report_path:
            c = canvas.Canvas(report_path, pagesize=letter)
            width, height = letter

            # Add title and date
            c.drawString(100, height - 50, "PDF Search Results")
            c.drawString(100, height - 70, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            c.drawString(100, height - 90, "Search Term: " + search_term_var.get())
            c.drawString(100, height - 110, "Results:")
            current_y = height - 130
            max_width = width - 200  # Set max width for text wrapping

            for page, line in found_results:
                # Prepare the result string
                result_string = f'Found on page {page}: {line}'
                current_y = draw_wrapped_text(c, result_string, 100, current_y, max_width)

                # Ensure a new line after each found result
                current_y -= 15  # Add space after each found line

            c.save()
            messagebox.showinfo("Report Generated", f"Report saved as: {report_path}")

# main window
root = tk.Tk()
root.title("PDF keyword finder")

# input values
pdf_file_path_var = tk.StringVar()
search_term_var = tk.StringVar()
case_sensitive_var = tk.BooleanVar()  # Variable for case sensitivity option

# creating widgets
tk.Label(root, text="PDF File:").grid(row=0, column=0, padx=5, pady=5)
tk.Entry(root, textvariable=pdf_file_path_var, width=50).grid(row=0, column=1, padx=5, pady=5)
tk.Button(root, text="Browse", command=browse_file).grid(row=0, column=2, padx=5, pady=5)

tk.Label(root, text="Search Term:").grid(row=1, column=0, padx=5, pady=5)
tk.Entry(root, textvariable=search_term_var, width=50).grid(row=1, column=1, padx=5, pady=5)

# Checkbox for case-sensitive
tk.Checkbutton(root, text="Case Sensitive", variable=case_sensitive_var).grid(row=2, column=0, columnspan=2, padx=5, pady=5)

tk.Button(root, text="Search", command=perform_search).grid(row=3, column=1, padx=5, pady=5)

# Button for saving the report
save_report_button = tk.Button(root, text="Save Report", command=save_report, state=tk.DISABLED)
save_report_button.grid(row=3, column=2, padx=5, pady=5)

# frame for the results text widget and scrollbar
results_frame = tk.Frame(root)
results_frame.grid(row=4, column=0, columnspan=3, padx=5, pady=5)

# Text widget to display results
results_text_widget = tk.Text(results_frame, wrap=tk.WORD, width=80, height=20)
results_text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Scrollbar for the text widget
scrollbar = tk.Scrollbar(results_frame, command=results_text_widget.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

results_text_widget.config(yscrollcommand=scrollbar.set)

# Global variable to hold the search results
found_results = []

root.mainloop()