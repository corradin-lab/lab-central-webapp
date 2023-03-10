import streamlit as st
from lab_central_webapp.peak_operations import get_peak_info_df
from lab_central_webapp.peak_to_gene import *
from lab_central_webapp.catalogs import IntakeCatalogWrapper
import lab_central_webapp
import pandas as pd
import rich
from rich import print
from functools import partial
import plotly.express as px
from pathlib import Path

st.set_page_config(layout="wide")

st.title("Linking peaks to genes")

col1, col2 = st.columns([2, 2])
col1.image("app/assets/peak_to_gene_illustration.png")
col1.caption("Image taken from https://www.engreitzlab.org/resources")
col2.image("app/assets/multiple_HiC_illustration.png")
col2.caption("Image adapted from https://flekschas.github.io/enhancer-gene-vis/")

st.subheader("Choose the options you want THEN upload the peaks file")

peaks_file = st.file_uploader("Upload your peaks file, file needs to be in tsv format and have no duplicated lines, and first 3 columns must be ['chrom', 'start', 'end']")
has_header = st.radio("Indicate if your file has a header line", ["File has header", "File does not have header"])

test = st.empty()
# st.write(hg38_HiC_catalog.catalog._entries.keys())
# st.write(dir(hg38_HiC_catalog))
HiC_files = list(hg38_HiC_catalog.catalog._entries.keys())
mode_dict = {"ensembl_all_genes_TSS_hg38": "closest", "ensembl_protein-coding_genes_TSS_hg38": "closest"}
maximum_kb_distance = 0

col1, col2 = st.columns([1, 3])
if peaks_file is not None:
    if has_header == "File has header":
        peaks_df = pd.read_csv(peaks_file, sep = "\t")
    else:
        peaks_df = pd.read_csv(peaks_file, sep = "\t", header = None)
    
    peaks_df.columns = ["chrom", "start", "end"] + list(peaks_df.columns[3:])
    num_unique_peaks = get_peak_info_df(peaks_df)['peak'].nunique()
    col1.write(peaks_df)
    col2.write(f"##### Number of rows: {peaks_df.shape[0]}, Number of unique peaks: {num_unique_peaks}")
    col2.write(f"##### Number of peaks per chromosome:")
    col2.write(peaks_df["chrom"].value_counts().to_frame().T)
    plot_df = peaks_df["chrom"].value_counts().to_frame()
    col2.plotly_chart(px.bar(plot_df, x= plot_df.columns))
    
#st.write(px.bar(peaks_df["chrom"].value_counts().to_frame()))
#need to fix this
hg38_HiC_catalog = IntakeCatalogWrapper(hg38_HiC_catalog_path, process_func = process_HiC)
ensembl_all_genes_TSS_hg38 = hg38_HiC_catalog.catalog["ensembl_all_genes_TSS_hg38"].read_and_process().set_index("gene").add_suffix("_TSS").reset_index()

HiC_used = st.multiselect("Select HiC files to use",  options = [*HiC_files, "combined"], default = ['PCHIC_Geschwind_NeuN+_hg38', "combined", "ensembl_all_genes_TSS_hg38"])

if "combined" in HiC_used:
     HiC_combined = st.multiselect("Select HiC files to combine",  options = HiC_files, default = ['PCHIC_Geschwind_NeuN+_hg38', 'PCHIC_per_tissue_Dorsolateral_Prefrontal_Cortex_hg38', 'PCHIC_per_tissue_Hippocampus_hg38'])

if [file.startswith("ensembl_") for file in HiC_used]:
    maximum_kb_distance = st.number_input("Maximum distance for nearest gene in kb, if 0 then filter is not applied", min_value=0, max_value=None, step=1, value = 500,  help=None, on_change=None, args=None, kwargs=None, disabled=False, label_visibility="visible")


@st.cache()
def generate_HiC_set(peaks_df, HiC_used):
    if "combined" in HiC_used:
        other_HiC_datasets = [HiC for HiC in HiC_used if HiC != "combined"]
        other_HiC_datasets_dict = {dataset_name: hg38_HiC_catalog.catalog[dataset_name].read_and_process() for dataset_name in hg38_HiC_catalog.catalog._entries if dataset_name in other_HiC_datasets}
       
        combined_HiC_datasets = [hg38_HiC_catalog.catalog[dataset_name] for dataset_name in hg38_HiC_catalog.catalog._entries if dataset_name in HiC_combined]
        #combined_HiC_datasets
        combined_HiC_df = pd.concat([dataset.read_and_process() for dataset in combined_HiC_datasets])
        combined_HiC_df = combined_HiC_df.genomic_range.combine_files_and_rename(f"combined_{len(combined_HiC_datasets)}")
        used_HiC_set = HiCFileSet({**other_HiC_datasets_dict, "combined": combined_HiC_df})

    else:
        used_HiC_set = HiCFileSet({dataset_name: hg38_HiC_catalog.catalog[dataset_name].read_and_process() for dataset_name in hg38_HiC_catalog.catalog._entries if dataset_name in HiC_used})
    
    return used_HiC_set


used_HiC_set = generate_HiC_set(peaks_df,HiC_used)
intersect_result_dict = used_HiC_set.intersect_peaks(peaks_df, mode_dict = mode_dict, ensembl_gene_TSS = ensembl_all_genes_TSS_hg38)
intersect_result_dict_unfiltered = {name: result.mapped_peaks_and_genes_df for name, result in intersect_result_dict.items()}
if maximum_kb_distance:
    intersect_result_dict_filtered = {name: unfiltered_df.query(f"distance_from_peak_to_TSS_in_kb < {maximum_kb_distance}") for name, unfiltered_df in intersect_result_dict_unfiltered.items()}

    intersect_result_compare = HiCFileSet.from_dict_pair(intersect_result_dict_unfiltered, intersect_result_dict_filtered, distance_in_kb = maximum_kb_distance, filter_label = f"filtered_{maximum_kb_distance}kb")
else:
    intersect_result_compare = HiCFileSet(intersect_result_dict_unfiltered)


unfiltered_df = intersect_result_compare.unfiltered.combined_df


num_gene_in_dataset = unfiltered_df.gene.nunique()
num_gene_with_TSS_info = unfiltered_df.query("distance_from_peak_to_TSS_in_kb.notna()").gene.nunique()

all_genes_have_TSS_info = num_gene_in_dataset == num_gene_with_TSS_info
st.write(f"#### Number of gene in all datasets: **:red[{num_gene_in_dataset}]**. Number of genes with TSS information: **:red[{num_gene_with_TSS_info}]**")

if not all_genes_have_TSS_info:
    st.write("#### :red[Note that we don't have TSS information for some of the genes that linked to peaks], this will affect the filtering based on peak distance to gene TSS (genes with no TSS info and all its linked peaks will be filtered out). The final result file will be the :red[UNFILTERED] one.")

st_plotly = partial(st.plotly_chart, use_container_width=True)
st_plotly(intersect_result_compare.compare_num_peaks())
#st_plotly(intersect_result_compare.compare_num_regions())
st_plotly(intersect_result_compare.compare_num_genes())

#st.write(intersect_result_compare.num_peaks_per_gene_df)

st_plotly(intersect_result_compare.compare_peak_lengths())

st_plotly(intersect_result_compare.compare_num_peaks_per_gene())
st_plotly(intersect_result_compare.compare_num_peaks_per_gene(gene_with_peaks_in_all_HiC_only = True))

st_plotly(intersect_result_compare.gene_num_peaks_coef_variation())

st.write("#### Download final data")
unfiltered_df
download_file_name = f"peak_to_gene_result_{Path(peaks_file.name).stem}"
st.download_button("Download results", unfiltered_df.to_csv(sep = "\t", index = False).encode('utf-8'), download_file_name)

st.write("#### Citations of all the HiC data used:")
def export_citation(datasets, catalog):
    all_cite_datasets = {}
    for dataset in datasets:
        all_cite_datasets[dataset] = catalog[dataset].metadata["citation"]["citation"]
    return all_cite_datasets

all_cite_datasets = {}

for dataset in HiC_used:
    if dataset == "combined":
        citations_to_add = export_citation(HiC_combined, hg38_HiC_catalog.catalog)
    elif dataset.startswith("ensembl_"):
        continue
    else:
        citations_to_add = export_citation([dataset], hg38_HiC_catalog.catalog)
    all_cite_datasets = {**all_cite_datasets, **citations_to_add}

for dataset, citation in all_cite_datasets.items():
    st.write(f"Dataset name: **{dataset}**")
    st.write(f"Citation: *{citation}*")


# st.write(intersect_result_compare.combined_df)
# st.write(intersect_result_compare.combined_df[["gene", "num_datasets_with_peak_for_gene", "datasets_with_peak_for_gene"]].drop_duplicates())
# st.write(intersect_result_compare.filtered._get_gene_num_peaks_coef_variation_df("filter_5kb"))

# File "/Users/ahoang/Library/Caches/pypoetry/virtualenvs/lab-central-webapp-Qp41mXlL-py3.8/lib/python3.8/site-packages/streamlit/runtime/scriptrunner/script_runner.py", line 565, in _run_script
#     exec(code, module.__dict__)
# File "/Users/ahoang/Documents/Work/webapp/lab-central-webapp/app/app.py", line 60, in <module>
#     intersect_result_compare = HiCFileSet.from_dict_pair(intersect_result_dict_unfiltered, intersect_result_dict_filtered, distance_in_kb = maximum_kb_distance, filter_label = f"filtered_{maximum_kb_distance}kb")
# File "/Users/ahoang/Documents/Work/webapp/lab-central-webapp/src/lab_central_webapp/peak_to_gene.py", line 254, in from_dict_pair
#     combined_set.genes_num_peaks_coef_variation_df = filtered_set._get_gene_num_peaks_coef_variation_df()#pd.concat([unfiltered_set._get_gene_num_peaks_coef_variation_df(filter_status = "unfiltered"), filtered_set._get_gene_num_peaks_coef_variation_df(filter_status = filter_label)])
# File "/Users/ahoang/Documents/Work/webapp/lab-central-webapp/src/lab_central_webapp/peak_to_gene.py", line 331, in _get_gene_num_peaks_coef_variation_df
#     self.num_peaks_per_gene_df.agg(["median", "min", "max"], axis =1)], axis = 1)#.assign(filter_status = filter_status)
# File "/Users/ahoang/Library/Caches/pypoetry/virtualenvs/lab-central-webapp-Qp41mXlL-py3.8/lib/python3.8/site-packages/pandas/core/frame.py", line 9342, in aggregate
#     result = op.agg()
# File "/Users/ahoang/Library/Caches/pypoetry/virtualenvs/lab-central-webapp-Qp41mXlL-py3.8/lib/python3.8/site-packages/pandas/core/apply.py", line 776, in agg
#     result = super().agg()
# File "/Users/ahoang/Library/Caches/pypoetry/virtualenvs/lab-central-webapp-Qp41mXlL-py3.8/lib/python3.8/site-packages/pandas/core/apply.py", line 175, in agg
#     return self.agg_list_like()
# File "/Users/ahoang/Library/Caches/pypoetry/virtualenvs/lab-central-webapp-Qp41mXlL-py3.8/lib/python3.8/site-packages/pandas/core/apply.py", line 438, in agg_list_like
#     raise ValueError("no results")

