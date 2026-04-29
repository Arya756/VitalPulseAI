import json

file_path = '/Users/ayusharyan/Desktop/Global hackathon/ECG_Hackathon_Complete_Pipeline.ipynb'

with open(file_path, 'r') as f:
    nb = json.load(f)

for cell in nb['cells']:
    if 'source' in cell:
        new_source = []
        for line in cell['source']:
            # Replace the load_record function entirely to be bulletproof
            if "def load_record(" in line and "db_path" in line:
                new_source = [
                    "import os\n",
                    "import wfdb\n",
                    "\n",
                    "def load_record(record_name, db_path=DB_PATH, channel=0, duration_sec=None):\n",
                    "    \"\"\"Load a WFDB record, returning signal + metadata, downloading if missing.\"\"\"\n",
                    "    # Check if file exists, if not, download it on the fly\n",
                    "    if not os.path.exists(os.path.join(db_path, f'{record_name}.hea')):\n",
                    "        print(f'⚠️ Record {record_name} not found in {db_path}. Downloading now...')\n",
                    "        os.makedirs(db_path, exist_ok=True)\n",
                    "        wfdb.dl_database('mitdb', dl_dir=db_path, records=[record_name])\n",
                    "    \n",
                    "    rec = wfdb.rdrecord(f'{db_path}/{record_name}', channels=[channel])\n",
                    "    signal = rec.p_signal[:, 0]\n",
                    "    fs = rec.fs\n",
                    "    if duration_sec:\n",
                    "        signal = signal[:int(duration_sec * fs)]\n",
                    "    annotation = wfdb.rdann(f'{db_path}/{record_name}', 'atr')\n",
                    "    return signal, fs, annotation\n"
                ]
                # We replaced the whole function, so we should skip the old function body
                skip_mode = True
                break
        
        if 'skip_mode' in locals() and skip_mode:
            # We found the function, we replaced it. We need to handle the rest of the cell safely.
            # Actually, it's safer to just replace the whole cell containing "def load_record" 
            pass

# Let's do it safely by just finding the cell with load_record
for cell in nb['cells']:
    if 'source' in cell and any("def load_record(" in line for line in cell['source']):
        # Find the index of def load_record
        start_idx = -1
        end_idx = -1
        for i, line in enumerate(cell['source']):
            if "def load_record(" in line:
                start_idx = i
            if start_idx != -1 and "return signal, fs, annotation" in line:
                end_idx = i
                break
        
        if start_idx != -1 and end_idx != -1:
            new_func = [
                "import os\n",
                "import wfdb\n",
                "def load_record(record_name, db_path=DB_PATH, channel=0, duration_sec=None):\n",
                "    \"\"\"Load a WFDB record, returning signal + metadata, downloading if missing.\"\"\"\n",
                "    if not os.path.exists(os.path.join(db_path, f'{str(record_name)}.hea')):\n",
                "        print(f'⚠️ Record {record_name} missing from {db_path}. Downloading...')\n",
                "        os.makedirs(db_path, exist_ok=True)\n",
                "        wfdb.dl_database('mitdb', dl_dir=db_path, records=[str(record_name)])\n",
                "    \n",
                "    rec = wfdb.rdrecord(f'{db_path}/{record_name}', channels=[channel])\n",
                "    signal = rec.p_signal[:, 0]\n",
                "    fs = rec.fs\n",
                "    if duration_sec:\n",
                "        signal = signal[:int(duration_sec * fs)]\n",
                "    annotation = wfdb.rdann(f'{db_path}/{record_name}', 'atr')\n",
                "    return signal, fs, annotation\n"
            ]
            cell['source'] = cell['source'][:start_idx] + new_func + cell['source'][end_idx+1:]

with open(file_path, 'w') as f:
    json.dump(nb, f, indent=1)

print("Updated load_record to automatically download missing files.")
