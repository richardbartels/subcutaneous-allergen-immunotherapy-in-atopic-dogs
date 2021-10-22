#  Subcutaneous allergen immunotherapy in atopic dogs
This code belongs to the papers *Efficacy of subcutaneous allergen immunotherapy in atopic dogs: a retrospective study of 664 cases.* by Fennis et al.

The main results can be found in `notebooks/main.ipynb` (or `notebooks/main.html`).

## How to use this code
### Create a virtual environment
This ensures you are using the right packages.
```
conda env create -f environment.yml
source activate atopische_dermatitis
```

### Code
Run `jupyter notebook notebooks/main.py` to see the code that contains most results of the paper.
The notebooks uses various functions defined in `src/`.

## Data
Raw data is not included in the repository.

### Data dictionary
<table>
  <tr>
    <th>Variable</th>
    <th>Variable name</th> 
    <th>Format</th>
    <th>Allowed values</th>
    <th>Descriptions</th>
  </tr>
  <tr>
    <td>Referral clinic</td>
    <td>Kliniek</td> 
    <td>text</td>
    <td>MDC, UKG</td>
    <td>Clinic at which the patient was treated.</td> 
  </tr>
  <tr>
    <td>Patient ID</td>
    <td>Vetware nummer</td> 
    <td>numeric</td>
    <td>-</td>
    <td>Unique patient identifier</td>
  </tr>
  <tr>
    <td>Breed</td>
    <td>Ras</td> 
    <td>text</td>
    <td>-</td>
    <td>Dog breed</td>
  </tr>
  <tr>
    <td>Breed group</td>
    <td>Rasgroep</td> 
    <td>text</td>
    <td>-</td>
    <td>Breed groups used in the analysis.</td>
  </tr>
  <tr>
    <td>Sex</td>
    <td>Geslacht</td> 
    <td>text</td>
    <td>vrouw, vrouwelijk gecastreerd, man, mannelijk gecastreerd</td>
    <td>Sex and neuter states (gecastreerd = neutered).</td>
  </tr>
  <tr>
    <td>Birth datetime</td>
    <td>Geboortedatum</td> 
    <td>text</td>
    <td>-</td>
    <td>-</td>
  </tr>
  <tr>
    <td>Start datetime of ASIT treatment</td>
    <td>Start asit</td> 
    <td>text</td>
    <td>-</td>
    <td>-</td>
  </tr>
  <tr>
    <td>Age at start of asit</td>
    <td>Leeftijd start</td> 
    <td>numeric</td>
    <td>-</td>
    <td>Age in years</td>
  </tr>
  <tr>
    <td>Skin test</td>
    <td>&lt;x&gt_huidtest</td> 
    <td>numeric</td>
    <td>0 (no), 1 (yes)</td>
    <td>&lt;x&gt corresponds to various possible allergens tested for.</td>
  </tr>
    <tr>
    <td>Serology</td>
    <td>&lt;x&gt_serologie</td> 
    <td>numeric</td>
    <td>0 (no), 1 (yes)</td>
    <td>&lt;x&gt corresponds to various possible allergens tested for.</td>
  </tr>
  <tr>
    <td>ASIT response (3 levels)</td>
    <td>Effectiviteit</td> 
    <td>numeric</td>
    <td>0 (poor), 1 (good), 2 (excellent)</td>
    <td>Corresponds to 0, 50% and 100% efficiency.</td>
  </tr>
  <tr>
    <td>ASIT response (2 levels)</td>
    <td>Effectiviteit 03</td> 
    <td>numeric</td>
    <td>0 (poor), 1 (good/excellent)</td>
    <td>Corresponds to 0 and 50%-100% efficiency.</td>
  </tr>
  <tr>
    <td>Regular re-examiniations</td>
    <td>Controle</td> 
    <td>numeric</td>
    <td>0 (no), 1 (yes)</td>
    <td>1 corresponds to at least one re-examination every 3 months during the first 9 months of treatment.</td>
  </tr>
  <tr>
    <td>Allergens included in AIT</td>
    <td>Therapie</td> 
    <td>text</td>
    <td>-</td>
    <td>Comma separated list</td>
  </tr>
</table>
