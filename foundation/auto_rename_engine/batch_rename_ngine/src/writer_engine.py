import os
import shutil

def execute_rename(rename_tasks, input_dir, output_dir):
    """Single writer yang bertanggung jawab mengubah status fisik file."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    print(f"Mengonversi {len(rename_tasks)} file...")
    
    for task in rename_tasks:
        src_path = os.path.join(input_dir, task["old_name"])
        dest_path = os.path.join(output_dir, task["new_name"])
        
        # Menggunakan shutil.copy atau os.rename. 
        # Disarankan copy ke folder output agar data master di folder input tetap aman (Idempotent).
        shutil.copy(src_path, dest_path)
        print(f"SUCCESS: [ {task['old_name']} ] -> [ {task['new_name']} ]")
        
    print("\nProses Batch Rename Selesai dengan Aman.")