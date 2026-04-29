import json

file_path = '/Users/ayusharyan/Desktop/Global hackathon/ECG_Hackathon_Complete_Pipeline.ipynb'

with open(file_path, 'r') as f:
    nb = json.load(f)

# Update the Data Config Cell with Auto-Discovery Logic
for cell in nb['cells']:
    if 'source' in cell and any('DATA CONFIGURATION' in line for line in cell['source']):
        new_source = [
            "# ─────────────────────────────────────────────────────────────────────────────\n",
            "# DATA CONFIGURATION (AUTO-DISCOVERY ENABLED)\n",
            "# ─────────────────────────────────────────────────────────────────────────────\n",
            "import os\n",
            "RECORDS = ['100', '101', '102', '103', '104', '105', '106', '107', '108', '109', '111', '112', '113', '114', '115', '116', '117', '118', '119', '121', '122', '123', '124', '200', '201', '202', '203', '205', '207', '208', '209', '210', '212', '213', '214', '215', '217', '219', '220', '221', '222', '223', '228', '230', '231', '232', '233', '234']\n",
            "\n",
            "# 🔍 AUTO-DISCOVERY: We will look for any folder containing '100.hea'\n",
            "DB_PATH = 'mitdb' # Default\n",
            "found_path = None\n",
            "\n",
            "for root, dirs, files in os.walk('/content'):\n",
            "    if '100.hea' in files:\n",
            "        found_path = root\n",
            "        break\n",
            "\n",
            "if found_path:\n",
            "    DB_PATH = found_path\n",
            "    print(f'✅ Found your database at: {DB_PATH}')\n",
            "else:\n",
            "    print(f'⚠️  Could not find local files. Falling back to downloading to {DB_PATH}...')\n",
            "    os.makedirs(DB_PATH, exist_ok=True)\n",
            "    try:\n",
            "        wfdb.dl_database('mitdb', dl_dir=DB_PATH, records=['100'])\n",
            "    except:\n",
            "        pass\n",
            "\n",
            "print(f'📊 Ready to process {len(RECORDS)} records.')\n"
        ]
        cell['source'] = new_source
        break

with open(file_path, 'w') as f:
    json.dump(nb, f, indent=1)

print("Notebook updated with Auto-Discovery logic.")
