try:
    print("Starting import...")
    import sys
    import tkinter as tk
    from app.main import App
    print("Imports successful")
    
    print("Creating app...")
    root = tk.Tk()
    root.geometry("520x1200")
    app = App(root)
    print("App created successfully")
    
    # Give it 2 seconds to run then close
    print("Running for 2 seconds...")
    root.after(2000, root.quit)
    root.mainloop()
    print("Mainloop exited successfully")
    
except Exception as e:
    print(f"\nError: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
finally:
    print("Done")
