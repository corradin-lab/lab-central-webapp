import streamlit as st
import pandas as pd
import seaborn as sns
import plotly.express as px
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="Integrate Peak Data",
    layout="wide",
)
st.set_option('deprecation.showPyplotGlobalUse', False)

st.title("Integrate Peak Data")
with st.expander("Reference image from brain scATAC paper"):
    st.image("app/assets/yang_etal_brain_scATAC_bioRxiv.png")
    st.caption("Image taken from https://www.biorxiv.org/content/10.1101/2022.11.09.515833v1.full.pdf")

st.selectbox("Choose source of data to integrate", options = ["bingren_brain_scATAC"])

all_control_peak_list_proportions_df = pd.read_csv("notebooks/package/ChIP_peaks_merge/all_control_peak_list_proportions_df.tsv", sep = "\t", index_col = 0)
peak_list = st.selectbox("Choose peak list", options = ["NAC_high_kmeans_pval_11", "GVEL_1tail_FDR05", "GVEL_2tail_FDR10",
                                                        "LVEL_1tail_FDR10",
                                                        "LVEL_1tail_FDR10_200kb",
                                                        "LVEL_1tail_FDR10_500kb",
                                                        "LVEL_2tail_FDR05", 
                                                        "LVEL_2tail_FDR05_extend_200kb",
                                                        "LVEL_2tail_FDR05_extend_500kb",
])



bingren_scATAC_result_clustered_reduced_52_cell_types_proportion_df = pd.read_csv(f"data/09_precomputed_scATAC/{peak_list}/bingren_scATAC_result_clustered_reduced_52_cell_types_proportion_df.tsv", index_col = 0, sep = "\t")
bingren_scATAC_result_reduced_52_cell_types_mean_proportion_df = pd.read_csv(f"data/09_precomputed_scATAC/{peak_list}/bingren_scATAC_result_reduced_52_cell_types_mean_proportion_df.tsv", index_col = 0, sep = "\t")
bingren_scATAC_result_mapped_peaks_cell_type_cols_unreduced = pd.read_csv(f"data/09_precomputed_scATAC/{peak_list}/bingren_scATAC_result_mapped_peaks_cell_type_cols_unreduced.tsv", index_col = 0, sep = "\t")

num_rows = bingren_scATAC_result_clustered_reduced_52_cell_types_proportion_df.shape[0]
num_unique_peaks = bingren_scATAC_result_clustered_reduced_52_cell_types_proportion_df.index.nunique()
if peak_list:
    st.write(f"##### Number of rows in list: {num_rows}. Number of unique peaks in list: {num_unique_peaks}")
if num_rows != num_unique_peaks:
    st.write(f"##### :red[WARNING]: Number of rows is different than number of unique peaks, this may cause error/wrong result. Please input list with unique peaks")


control_peaks = st.multiselect("Choose control peak list(s)", options = all_control_peak_list_proportions_df.columns.tolist(), default= "bingren_scATAC_all_data")
one_row_per_peak_binary_df = (bingren_scATAC_result_mapped_peaks_cell_type_cols_unreduced.groupby(level = 0).sum() >= 1).astype(int)

st.write("#### Raw 107 cell types binary matrix")
st.write(one_row_per_peak_binary_df.loc[bingren_scATAC_result_clustered_reduced_52_cell_types_proportion_df.index,:], use_container_width=True)
st.write("#### Grouped 52 cell types continuous matrix")
st.write(bingren_scATAC_result_clustered_reduced_52_cell_types_proportion_df[sorted(bingren_scATAC_result_clustered_reduced_52_cell_types_proportion_df.columns.tolist())], use_container_width=True)


#fig = plt.figure(figsize=(20, 10))
# sns.clustermap(bingren_scATAC_result_mapped_peaks_cell_type_cols_unreduced[["MSN_1", "MSN_2", "MSN_3"]],figsize=(20, 10))
# st.pyplot()


proportion_peaks_active_df = (one_row_per_peak_binary_df.sum().to_frame(name = peak_list)/ num_unique_peaks) * 100

cluster_one_row_per_peak_binary_df = sns.clustermap(one_row_per_peak_binary_df)



st.write("#### Percentage of peaks that are active in each cell type")
st.plotly_chart(px.bar(proportion_peaks_active_df,  title = "Cell types organized by alphabetical order"), use_container_width = True)

st.plotly_chart(px.bar(proportion_peaks_active_df.loc[cluster_one_row_per_peak_binary_df.data2d.columns.tolist(),:],  title = "Cell types organized by clustering order"), use_container_width = True)

heatmap_plot_df = pd.concat([bingren_scATAC_result_clustered_reduced_52_cell_types_proportion_df, one_row_per_peak_binary_df], axis = 1)

st.write("#### Heatmap of peaks (rows) and 52 cell types (columns)")
with st.form("Heatmap options"):
    st.write("##### Select columns to display then click `Generate Heatmap`")
    heatmap_cols = st.multiselect("Select the cell type columns to visualize on heatmap:", options = sorted(heatmap_plot_df.columns.tolist()), default = sorted(bingren_scATAC_result_clustered_reduced_52_cell_types_proportion_df.columns.tolist()))
    updated_heatmap = st.form_submit_button("Generate heatmap")
    
    if updated_heatmap:
        heatmap_data = sns.clustermap(heatmap_plot_df[heatmap_cols],figsize=(20, 10))
        st.pyplot()
        st.plotly_chart(px.imshow(heatmap_data.data2d\
                                  .reset_index(drop= True)), use_container_width = True)



st.write("#### Distribution of cell types in active peaks")
plot_df = pd.concat([bingren_scATAC_result_reduced_52_cell_types_mean_proportion_df,all_control_peak_list_proportions_df[control_peaks]],axis = 1)
plot_df_with_difference = plot_df.assign(difference = (plot_df.subtract(plot_df[peak_list], axis =0)).abs().sum(axis=1)/plot_df[peak_list]).sort_values("difference", ascending = False)
st.plotly_chart(px.bar(plot_df_with_difference, x= plot_df_with_difference.index, y = plot_df.columns, barmode = "group", title = f"Relative proportion of cell type for each peak list, ordered by magnitude of ABSOLUTE difference to list `{peak_list}`"), use_container_width = True)

plot_df_with_difference = plot_df.assign(difference = (plot_df.subtract(plot_df[peak_list], axis =0)).max(axis=1)/plot_df[peak_list]).sort_values("difference", ascending = False)
st.plotly_chart(px.bar(plot_df_with_difference, x= plot_df_with_difference.index, y = plot_df.columns, barmode = "group", title = f"Relative proportion of cell type for each peak list, ordered by magnitude of MAX difference to list `{peak_list}`"), use_container_width = True)

# plot_df_with_difference = plot_df.assign(difference = (plot_df.subtract(plot_df[peak_list], axis =0)).min(axis=1)/plot_df[peak_list]).sort_values("difference", ascending = False)
# st.plotly_chart(px.bar(plot_df_with_difference, x= plot_df_with_difference.index, y = plot_df.columns, barmode = "group", title = f"Relative proportion of cell type for each peak list, ordered by magnitude of MIN difference to list `{peak_list}`"), use_container_width = True)