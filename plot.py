import pandas as pd
#with this import sequence enable using ttk widgets.
from tkinter import ttk
from tkinter import *
from tkinter.ttk import *
from tkinter import filedialog
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.dates import num2date
import numpy as np
    
def selected_channels(lb_columns, lb_selected_col, cols_y):
    selected = [key for key,[i, var1, var2] in openrvdata.selected_cols.items() if i in lb_columns.curselection()]   
    if cols_y.get() == '':
        for key in selected:
            openrvdata.selected_cols[key][1]=True
            openrvdata.selected_cols[key][2]=True
    else:
        for key in openrvdata.selected_cols.keys():
            if openrvdata.selected_cols[key][2]:
                openrvdata.selected_cols[key][1]=openrvdata.selected_cols[key][2]
        for key in selected:
            openrvdata.selected_cols[key][1]=True
    final=[key for key,[i,var1,var2] in openrvdata.selected_cols.items() if var1 == True]
    cols_y.set(final)
    lb_selected_col.update()
    
def remove_all(lb_selected_col, cols_y):
    for key in openrvdata.selected_cols.keys():
        openrvdata.selected_cols[key][1]=False
        openrvdata.selected_cols[key][2]=False
    cols_y.set('')
        
def remove_selected(lb_selected_col, cols_y):
    selected = [key for key,[i,var1,var2] in openrvdata.selected_cols.items() if var1 == True]
    removed = [i for i in lb_selected_col.curselection()]
    for i in sorted(removed, reverse=True):
        openrvdata.selected_cols[selected[i]][1] = False
        openrvdata.selected_cols[selected[i]][2] = False
        del selected[i]
    cols_y.set(selected)
    lb_selected_col.update()
    
def plot_rv(twn_time, log_scale):
    
    if plt.get_fignums(): # if there is any existed figures will be closed.
        plt.close('all')
        
    fig, ax = plt.subplots()
    log_plot=log_scale.get()
    
    # Plot the selected columns using the specified x-axis column and log scale for y-axis
    plot_rv.selected = [key for key,[i,var1,var2] in openrvdata.selected_cols.items() if var1 == True]
    
    if twn_time.get():
        openrvdata.df['TWN Time'] = openrvdata.df['Date UTC'] + pd.to_timedelta('8h')
        plot_rv.time = 'TWN Time'
        for cols in plot_rv.selected:
            ax.plot(openrvdata.df['TWN Time'], openrvdata.df[cols], 'o-', label=cols)
            plt.xlabel('TWN Time')
    else:
        plot_rv.time = 'Date UTC'
        for cols in plot_rv.selected:
            ax.plot(openrvdata.df['Date UTC'], openrvdata.df[cols], 'o-', label=cols)
            plt.xlabel('UTC Time')
    
    if log_scale.get():
        ax.set_yscale('log')
    
    coords = []     
    ax.legend()
    
    #For plot start and end cursors repeatedly 
    
    global cid
    
    cid = fig.canvas.mpl_connect('button_press_event', lambda event: right_click(event, fig, ax))

    plt.show()

def openrvdata(lb_columns,ava_cols):
    file_path = filedialog.askopenfilename(
        title="Open a File",
        filetypes=(("csv files", "*.csv"), ("All files", "*.*"))
    )
    
    # If a file is selected
    if file_path:
        try:
            openrvdata.df = pd.read_csv(file_path)
            openrvdata.selected_cols={key:[i, False, False] for i, key in enumerate(openrvdata.df.columns.tolist(),start=-1)}
            del openrvdata.selected_cols['Date UTC']
            openrvdata.df['Date UTC'] = pd.to_datetime(openrvdata.df['Date UTC'], format='mixed')
            ava_cols.set(list(openrvdata.selected_cols.keys()))
            lb_columns.update()

        except Exception as e:
            messagebox.showerror("Error", f"Could not open file: {e}")
            return None, None


def right_click(event, fig, ax):
    """Updates the start and end cursors based on mouse clicks."""

    global click_state, cursor_a, cursor_b, cursor_a_line, cursor_b_line

    if event.button == 3:  # Right mouse button
        if event.inaxes == ax:  # Ensure click happens inside the axes
            if click_state:  # First click to add or update cursor_start
                
                cursor_ax, nt_y = nearby(event.xdata, event.ydata, plot_rv.selected, plot_rv.time, openrvdata.df)

                # Remove the existing start line and annotation if they exist
                if cursor_a_line:
                    for item in cursor_a_line:
                        item.remove()  # Properly remove Line2D and Annotation objects
                    cursor_a_line = []

                # Add new vertical line and annotation for cursor_start
                cursor_a_line = [
                    ax.axvline(x=cursor_ax, color='red', linestyle='--', label='A'),
                    ax.annotate(
                        f"X: {cursor_ax.strftime('%Y-%m-%d %H:%M:%S')}\nY: {nt_y:.3f}",
                        xy=(cursor_ax, nt_y), xycoords='data',
                        xytext=(10, 10), textcoords='offset points',
                        bbox=dict(boxstyle="round,pad=0.3", edgecolor='black', facecolor='white', alpha=0.7)
                    )
                ]
                ax.legend()
                fig.canvas.draw()  # Redraw the canvas to show cursor_start
                click_state = False  # Toggle to add or update cursor_end on next click

            else:  # Second click to add or update cursor_end
                cursor_bx, nt_y = nearby(event.xdata, event.ydata, plot_rv.selected, plot_rv.time, openrvdata.df)
                #cursor_b = num2date(event.xdata).replace(tzinfo=None)

                # Remove the existing end line and annotation if they exist
                if cursor_b_line:
                    for item in cursor_b_line:
                        item.remove()  # Properly remove Line2D and Annotation objects
                    cursor_b_line = []

                # Add new vertical line and annotation for cursor_end
                cursor_b_line = [
                    ax.axvline(x=cursor_bx, color='blue', linestyle='--', label='B'),
                    ax.annotate(
                        f"X: {cursor_bx.strftime('%Y-%m-%d %H:%M:%S')}\nY: {nt_y:.3f}",
                        xy=(cursor_bx, nt_y), xycoords='data',
                        xytext=(10, 10), textcoords='offset points',
                        bbox=dict(boxstyle="round,pad=0.3", edgecolor='black', facecolor='white', alpha=0.7)
                    )
                ]
                ax.legend()
                fig.canvas.draw()  # Redraw the canvas to show cursor_end
                click_state = True  # Reset back to updating cursor_start on next click

def nearby(curx, cury, mark_col, time_col, rvdf):  
    
    curx = num2date(curx).replace(tzinfo=None)
    y_value_time_index = rvdf.loc[rvdf[mark_col[0]].notna()].index #get index of the data column which has values.
    nearby_time = abs(rvdf[time_col].loc[y_value_time_index] - curx) #find out the nearst datetime based on cursor position.
    
    min_index = nearby_time.idxmin()
    nearest_y = rvdf.loc[min_index, mark_col[0]]
    nearest_x = rvdf.loc[min_index, time_col]

    return nearest_x, nearest_y

def main():
    root=Tk()
    root.title("RV Plot")
    root.grid_rowconfigure(1, weight=1)
    root.grid_columnconfigure([0,1], weight=1)
    root.option_add('*tearOFF',False)  
    
    frame_col=ttk.Labelframe(root,padding='5 5 7 10',text='Available Channels')
    frame_col.grid(row=1, column=0, sticky="nsew")
    frame_col.grid_rowconfigure([1,2,3],weight=1)
    frame_col.grid_columnconfigure(0,weight=1)
    
    frame_sel=ttk.Labelframe(root,padding='5 5 7 10',text='Selected Channels')
    frame_sel.grid(row=1, column=1, sticky="nsew")
    frame_sel.grid_rowconfigure([1,2,3],weight=1)
    frame_sel.grid_columnconfigure(0,weight=1)
        
    frame_butt=ttk.Frame(root,padding='5 5 10 10')
    frame_butt.grid(row=1, column=2)
    frame_butt.grid_rowconfigure(0,weight=1)
    frame_butt.grid_columnconfigure(0,weight=1)
    
    #variables for the GUI
    ava_cols=StringVar() 
    cols_y=StringVar()
    log_scale=BooleanVar() 
    twn_time=BooleanVar()
    rvinfo=StringVar()
    
    #information window
    rvdata_time=ttk.Label(root,textvariable=rvinfo,padding='5 5 5 5')
    rvinfo.set('Cursor position testing now')
    rvdata_time.grid(row=0,column=0,columnspan=3,sticky='ew')
    
    # Available columns listbox
    lb_columns = Listbox(frame_col, listvariable=ava_cols, selectmode='extended')
    lb_columns.grid(row=1,column=0, rowspan=3,sticky='nsew')
    lb_columns_sb = ttk.Scrollbar(frame_col, orient='vertical', command=lb_columns.yview)
    lb_columns.config(yscrollcommand=lb_columns_sb.set)
    lb_columns_sb.grid(row=1,column=1,rowspan=3,sticky='ns')
    
    # Selected columns listbox
    lb_selected_col = Listbox(frame_sel, listvariable=cols_y, selectmode='extended')
    lb_selected_col.grid(row=1,column=0,rowspan=3,sticky='nsew')
    lb_selected_col_sb = ttk.Scrollbar(frame_sel, orient='vertical', command=lb_selected_col.yview)
    lb_selected_col.config(yscrollcommand=lb_selected_col_sb.set)
    lb_selected_col_sb.grid(row=1,column=1,rowspan=3,sticky='ns')    
    
    # Buttons
    Button(frame_butt, text='Add', command=lambda: selected_channels(lb_columns, lb_selected_col, cols_y)).grid(row=1)
    Button(frame_butt, text='Remove', command=lambda: remove_selected(lb_selected_col, cols_y)).grid(row=2)
    Button(frame_butt, text='Remove All', command=lambda: remove_all(lb_selected_col, cols_y)).grid(row=3)   
    Button(frame_butt, text='Plot', command=lambda: plot_rv(twn_time, log_scale)).grid(row=4)
        
    # Checkbox for log scale and plot with TWN time
    Checkbutton(frame_butt, text="Log scale", variable=log_scale, onvalue = True, offvalue = False).grid(row=5)
    Checkbutton(frame_butt, text='TWN Time', variable=twn_time, onvalue = True, offvalue = False).grid(row=6)
    
    #create a menu for opening file
    menu_of=Menu(root)
    menu_of.add_command(label='Open',command=lambda: openrvdata(lb_columns, ava_cols))
    root.config(menu=menu_of)
    
    root.mainloop()

# These are for setting up interactivate figure functions
click_state = True
cursor_a = None
cursor_b = None
cursor_a_line = None
cursor_b_line = None        


if __name__ == "__main__":
    # These are for setting up interactivate figure functions
    click_state = True
    cursor_start = None
    cursor_end = None
    cursor_start_line = None
    cursor_end_line = None
    
    main()