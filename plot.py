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
    
    #For plot start and end cursors repeatedly with "right_click" function.
    fig.canvas.mpl_connect('button_press_event', lambda event: right_click_menu(event, fig, ax))
    
    plot_rv.cura = False
    plot_rv.curb = False
    marker.cur_a_line = []
    marker.cur_b_line = []
    plt.show()
    #%matplotlib
    #plt.pause()

def openrvdata(lb_columns, ava_cols, lb_selected_col, cols_y):
    
    ava_cols.set('')
    lb_columns.update()
    cols_y.set('')
    lb_selected_col.update()
    
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


def marker(event, fig, ax, curs):
    """Updates the start and end cursors based on mouse clicks."""

    if curs == 'A':
        cursor_ax, nt_y = nearby(event.xdata, event.ydata, plot_rv.selected, plot_rv.time, openrvdata.df)
        # Remove the existing end line and annotation if they exist
        if plot_rv.cura:
            for item in marker.cur_a_line:
                item.remove()  # Properly remove Line2D and Annotation objects
            marker.cur_a_line = []
            
        # Add new vertical line and annotation for cursor_end
        marker.cur_a_line = [
            ax.axvline(x=cursor_ax, color='blue', linestyle='--', label='A'),
            ax.annotate(
               f"X: {cursor_ax.strftime('%Y-%m-%d %H:%M:%S')}\nY: {nt_y:.3f}",
               xy=(cursor_ax, nt_y), xycoords='data',
               xytext=(10, 10), textcoords='offset points',
               bbox=dict(boxstyle="round,pad=0.3", edgecolor='black', facecolor='white', alpha=0.7))
                    ]

        plot_rv.cura = True  # True, if there is cursor A in the plot.
        
    elif curs == 'B':
        cursor_bx, nt_y = nearby(event.xdata, event.ydata, plot_rv.selected, plot_rv.time, openrvdata.df)
        # Remove the existing start line and annotation if they exist
        if plot_rv.curb:
            for item in marker.cur_b_line:
                item.remove()  # Properly remove Line2D and Annotation objects
            marker.cur_b_line = []
            
        # Add new vertical line and annotation for cursor_start
        marker.cur_b_line = [
            ax.axvline(x=cursor_bx, color='red', linestyle='--', label='B'),
            ax.annotate(
                f"X: {cursor_bx.strftime('%Y-%m-%d %H:%M:%S')}\nY: {nt_y:.3f}",
                xy=(cursor_bx, nt_y), xycoords='data',
                xytext=(10, 10), textcoords='offset points',
                bbox=dict(boxstyle="round,pad=0.3", edgecolor='black', facecolor='white', alpha=0.7))
                    ]
            
        plot_rv.curb = True  # True, if there is cursor B in the plot
    
    elif curs == 'ra':
        
        for item in marker.cur_a_line:
            item.remove()  # Properly remove Line2D and Annotation objects
        marker.cur_a_line = []
        plot_rv.cura = False
        
    elif curs == 'rb':
        for item in marker.cur_b_line:
            item.remove()  # Properly remove Line2D and Annotation objects
        marker.cur_b_line = []
        plot_rv.curb = False

    elif curs == 'rall':
        for item in marker.cur_a_line + marker.cur_b_line:
            item.remove()  # Properly remove Line2D and Annotation objects
        marker.cur_a_line = []
        marker.cur_b_line = []
        plot_rv.cura = False
        plot_rv.curb = False

    else:
        print('Life is nothing but an electron looking for a place to rest.\n')
    
    ax.legend()
    fig.canvas.draw()  # Redraw the canvas to show cursor_end


def right_click_menu(event, fig, ax):
    #right_click_menu
    if event.button == 3:
        if event.inaxes == ax:  # Ensure click happens inside the axes
            menu_rclick =  Menu(fig.canvas.get_tk_widget(), tearoff=0)
            menu_rclick.add_command(label='Add Cursor A', command=lambda: marker(event, fig, ax, 'A'))
            menu_rclick.add_command(label='Add Cursor B', command=lambda: marker(event, fig, ax, 'B'))
            menu_rclick.add_command(label="Remove Cursor A", command=lambda: marker(event, fig, ax, 'ra'))
            menu_rclick.add_command(label="Remove Cursor B", command=lambda: marker(event, fig, ax, 'rb'))
            menu_rclick.add_command(label="Remove Cursors", command=lambda: marker(event, fig, ax, 'rall'))
            menu_rclick.post(event.guiEvent.x_root, event.guiEvent.y_root)


def nearby(curx, cury, mark_col, time_col, rvdf):  
    
    curx = num2date(curx).replace(tzinfo=None)
    y_value_time_index = rvdf.loc[rvdf[mark_col[0]].notna()].index #get index of the data column which has values.
    nearby_time = abs(rvdf[time_col].loc[y_value_time_index] - curx) #find out the nearst datetime based on cursor position.
    
    min_index = nearby_time.idxmin()
    nearest_y = rvdf.loc[min_index, mark_col[0]]
    nearest_x = rvdf.loc[min_index, time_col]

    return nearest_x, nearest_y
        
def plot_all():
    # Asking input a data range and zoom-in then plot every channels and save it. 
    for cols in plot_rv.selected:
        fig, ax = plt.subplots()
        ax.plot(openrvdata.df['Date UTC'], openrvdata.df[cols], 'o-', label=cols)
    
    plt.xlabel('UTC Time')
    ax.legend()
    plt.show()
    
def help_plot():
    #showing help message about how to use this script.
    print('help')

def main():
    root=Tk()
    root.title("RV Plot")
    root.grid_rowconfigure(1, weight=1)
    root.grid_columnconfigure([0,1], weight=1)
    root.option_add('*tearOFF',False)  
    
    #create a menu for opening file
    menu_bar=Menu(root)
    menu_bar=Menu(menu_bar,tearoff=0)
    menu_bar.add_command(label='Open',command=lambda: openrvdata(lb_columns, ava_cols, lb_selected_col, cols_y))
    menu_bar.add_command(label="I'm lazy", command=lambda: plot_all())
    menu_bar.add_command(label='Help', command=lambda: help_plot())
    root.config(menu=menu_bar)
    
    #variables for the GUI
    ava_cols=StringVar() 
    cols_y=StringVar()
    log_scale=BooleanVar() 
    twn_time=BooleanVar()
    rvinfo=StringVar()
    
    #space for easy to read GUI
    rvdata_time=ttk.Label(root,textvariable=rvinfo,padding='5 5 5 5')
    rvinfo.set('')
    rvdata_time.grid(row=0,column=0,columnspan=3,sticky='ew')  
    
    # Available columns setup
    frame_col=ttk.Labelframe(root,padding='5 5 7 10',text='Available Channels')
    frame_col.grid(row=1, column=0, sticky="nsew")
    frame_col.grid_rowconfigure([1,2,3],weight=1)
    frame_col.grid_columnconfigure(0,weight=1)
       
    lb_columns = Listbox(frame_col, listvariable=ava_cols, selectmode='extended')
    lb_columns.grid(row=1,column=0, rowspan=3,sticky='nsew')
    lb_columns_sb = ttk.Scrollbar(frame_col, orient='vertical', command=lb_columns.yview)
    lb_columns.config(yscrollcommand=lb_columns_sb.set)
    lb_columns_sb.grid(row=1,column=1,rowspan=3,sticky='ns')
    
    #Selected Channels column setup 
    frame_sel=ttk.Labelframe(root,padding='5 5 7 10',text='Selected Channels')
    frame_sel.grid(row=1, column=1, sticky="nsew")
    frame_sel.grid_rowconfigure([1,2,3],weight=1)
    frame_sel.grid_columnconfigure(0,weight=1)

    lb_selected_col = Listbox(frame_sel, listvariable=cols_y, selectmode='extended')
    lb_selected_col.grid(row=1,column=0,rowspan=3,sticky='nsew')
    lb_selected_col_sb = ttk.Scrollbar(frame_sel, orient='vertical', command=lb_selected_col.yview)
    lb_selected_col.config(yscrollcommand=lb_selected_col_sb.set)
    lb_selected_col_sb.grid(row=1,column=1,rowspan=3,sticky='ns')    

    #Buttons and clickboxes setup  
    frame_butt=ttk.Frame(root,padding='5 5 10 10')
    frame_butt.grid(row=1, column=2)
    frame_butt.grid_rowconfigure(0,weight=1)
    frame_butt.grid_columnconfigure(0,weight=1)
    
    Button(frame_butt, text='Add', command=lambda: selected_channels(lb_columns, lb_selected_col, cols_y)).grid(row=1)
    Button(frame_butt, text='Remove', command=lambda: remove_selected(lb_selected_col, cols_y)).grid(row=2)
    Button(frame_butt, text='Remove All', command=lambda: remove_all(lb_selected_col, cols_y)).grid(row=3)   
    Button(frame_butt, text='Plot', command=lambda: plot_rv(twn_time, log_scale)).grid(row=4)
    #Button(frame_butt, text='Remove Cursors',command=lambda: remove_cursor(fig,ax)).grid(row=5)
   
    # Checkbox for log scale and plot with TWN time
    Checkbutton(frame_butt, text="Log scale", variable=log_scale, onvalue = True, offvalue = False).grid(row=6)
    Checkbutton(frame_butt, text='TWN Time', variable=twn_time, onvalue = True, offvalue = False).grid(row=7)
    
    root.mainloop()     

if __name__ == "__main__":
    main()
