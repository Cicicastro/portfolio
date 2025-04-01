import gradio as gr
import pandas as pd
import plotly.express as px
import scipy.stats as stats

# Load datasets
df_cross = pd.read_csv("oasis_cross-sectional-processed.csv")
df_long = pd.read_csv("oasis_longitudinal-processed.csv")

# Standardize column names
df_long.rename(columns={"EDUC": "Educ"}, inplace=True)
df_cross.rename(columns={"EDUC": "Educ"}, inplace=True)

# Prepare datasets
df_long["Condition"] = df_long["Group"]
df_long = df_long[df_long["Condition"].isin(["Nondemented", "Demented"])]
df_cross["Condition"] = df_cross["CDR"].apply(lambda x: "Healthy" if x == 0 else "Alzheimer")

# Define custom color palette
custom_palette = {"Healthy": "#1f77b4", "Alzheimer": "#ff7f0e", "Nondemented": "#1f77b4", "Demented": "#ff7f0e"}

# Function to generate graphs
def generate_graphs(dataset):
    df = df_cross if dataset == "Cross-Sectional" else df_long
    condition_healthy = "Nondemented" if dataset == "Longitudinal" else "Healthy"
    condition_demented = "Demented" if dataset == "Longitudinal" else "Alzheimer"

    # Generate figures
    fig_age = px.histogram(df, x="Age", color="Condition", nbins=15, opacity=0.6, barmode="overlay",
                           title="Age Distribution", color_discrete_map=custom_palette)

    fig_educ = px.histogram(df, x="Educ", color="Condition", nbins=10, opacity=0.6, barmode="overlay",
                            title="Education Level Distribution", color_discrete_map=custom_palette)

    fig_ses = px.histogram(df, x="SES", color="Condition", nbins=5, opacity=0.6, barmode="overlay",
                           title="Socioeconomic Status Distribution", color_discrete_map=custom_palette)

    fig_nwbv = px.histogram(df, x="nWBV", color="Condition", nbins=20, opacity=0.6, barmode="overlay",
                            title="Brain Volume Distribution", color_discrete_map=custom_palette)

    fig_nwbv_boxplot = px.box(df, x="Condition", y="nWBV", color="Condition",
                               title="Brain Volume Boxplot", color_discrete_map=custom_palette)

    # Calculate gender prevalence
    total_gender_counts = df["M/F"].value_counts()
    demented_gender_counts = df[df["Condition"] == condition_demented]["M/F"].value_counts()
    prevalence_percentage = (demented_gender_counts / total_gender_counts) * 100

    fig_gender_prevalence = px.bar(
        x=prevalence_percentage.index,
        y=prevalence_percentage.values,
        color=prevalence_percentage.index,
        title="Prevalence of Alzheimer's by Gender (Percentage)",
        labels={"x": "Gender", "y": "Percentage of Demented Cases"},
        color_discrete_map={"M": "#1f77b4", "F": "#ff7f0e"}
    )

    # Calculate p-values
    age_pval = stats.ttest_ind(df[df["Condition"] == condition_healthy]["Age"],
                               df[df["Condition"] == condition_demented]["Age"], nan_policy="omit").pvalue

    educ_pval = stats.ttest_ind(df[df["Condition"] == condition_healthy]["Educ"],
                                df[df["Condition"] == condition_demented]["Educ"], nan_policy="omit").pvalue

    ses_pval = stats.ttest_ind(df[df["Condition"] == condition_healthy]["SES"],
                               df[df["Condition"] == condition_demented]["SES"], nan_policy="omit").pvalue

    nwbv_pval = stats.ttest_ind(df[df["Condition"] == condition_healthy]["nWBV"],
                                df[df["Condition"] == condition_demented]["nWBV"], nan_policy="omit").pvalue

    chi2, gender_pval, _, _ = stats.chi2_contingency(pd.crosstab(df["M/F"], df["Condition"]))

    # P-Value Annotations
    p_value_age = f"**p-value: {age_pval:.5f}**"
    p_value_educ = f"**p-value: {educ_pval:.5f}**"
    p_value_ses = f"**p-value: {ses_pval:.5f}**"
    p_value_nwbv = f"**p-value: {nwbv_pval:.5f}**"
    p_value_gender = f"**p-value: {gender_pval:.5f}**"

    return (fig_age, p_value_age, fig_educ, p_value_educ, fig_ses, p_value_ses,
            fig_gender_prevalence, p_value_gender, fig_nwbv, p_value_nwbv, fig_nwbv_boxplot)

# Load default Cross-Sectional dataset on startup
default_graphs = generate_graphs("Cross-Sectional")

# Create Gradio UI
with gr.Blocks() as demo:
    gr.Markdown("# Alzheimer Analysis Dashboard")

    dataset_choice = gr.Radio(["Cross-Sectional", "Longitudinal"], value="Cross-Sectional", label="Select Dataset")

    with gr.Row():
        with gr.Column():
            output_age = gr.Plot(value=default_graphs[0], label="Age Distribution")
            output_pval_age = gr.Markdown(value=default_graphs[1])
        with gr.Column():
            output_educ = gr.Plot(value=default_graphs[2], label="Education Level Distribution")
            output_pval_educ = gr.Markdown(value=default_graphs[3])

    with gr.Row():
        with gr.Column():
            output_ses = gr.Plot(value=default_graphs[4], label="Socioeconomic Status Distribution")
            output_pval_ses = gr.Markdown(value=default_graphs[5])
        with gr.Column():
            output_gender = gr.Plot(value=default_graphs[6], label="Prevalence of Alzheimer's by Gender")
            output_pval_gender = gr.Markdown(value=default_graphs[7])

    with gr.Row():
        with gr.Column():
            output_nwbv = gr.Plot(value=default_graphs[8], label="Brain Volume Distribution")
            output_pval_nwbv = gr.Markdown(value=default_graphs[9])
        with gr.Column():
            output_nwbv_box = gr.Plot(value=default_graphs[10], label="Brain Volume Boxplot")

    def update_graphs(dataset):
        """ Update the graphs when dataset is changed """
        graphs = generate_graphs(dataset)
        return graphs

    dataset_choice.change(update_graphs, 
                          inputs=dataset_choice, 
                          outputs=[output_age, output_pval_age, output_educ, output_pval_educ,
                                   output_ses, output_pval_ses, output_gender, output_pval_gender,
                                   output_nwbv, output_pval_nwbv, output_nwbv_box])

demo.launch()