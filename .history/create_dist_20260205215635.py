import tarfile
import os

def create_linux_dist():
    output_filename = "TB2ASJ_Linux_Source.tar.gz"
    source_dir = os.getcwd()
    
    # Dışlanacak klasörler ve dosyalar
    excludes = {
        'venv', '.git', '.idea', '__pycache__', 'dist', 'build', 
        'TB2ASJ_Telsiz.spec', output_filename, '.vscode', 'pytest_cache'
    }
    
    print(f"Paket oluşturuluyor: {output_filename}...")
    
    with tarfile.open(output_filename, "w:gz") as tar:
        for root, dirs, files in os.walk(source_dir):
            # Dışlanan klasörleri yerinde filtrele
            dirs[:] = [d for d in dirs if d not in excludes]
            
            for file in files:
                if file.endswith(('.pyc', '.pyo', '.pyd', '.exe', '.ds_store')):
                    continue
                if file == output_filename:
                    continue
                if file.endswith(".spec"):
                    continue
                    
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, source_dir)
                
                # Arşivin içine 'TB2ASJ_Telsiz' ana klasörü ile koy
                # Böylece çıkarınca ortalığa saçılmaz
                arcname = os.path.join("TB2ASJ_Telsiz", rel_path)
                
                print(f"Eklendi: {rel_path}")
                tar.add(full_path, arcname=arcname)
                
    print("\n✅ İşlem tamamlandı!")
    print(f"Dosya hazır: {os.path.abspath(output_filename)}")

if __name__ == "__main__":
    create_linux_dist()
