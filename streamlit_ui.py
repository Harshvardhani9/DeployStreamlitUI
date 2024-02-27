import streamlit as st
import os
import json
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import re

# Function to generate HTML for hover tooltip
def generate_hover_tooltip(df):
    tooltip_script = """
        <script>
        function showTooltip(element, text) {
            var tooltip = document.getElementById("tooltip");
            tooltip.innerHTML = text;
            tooltip.style.display = "block";
            tooltip.style.left = (element.getBoundingClientRect().left + window.scrollX) + "px";
            tooltip.style.top = (element.getBoundingClientRect().top + window.scrollY - 30) + "px";
        }
        function hideTooltip() {
            var tooltip = document.getElementById("tooltip");
            tooltip.style.display = "none";
        }
        </script>
    """
    tooltip_div = """<div id="tooltip" style="display:none; position: absolute; background: lightgray; padding: 5px; border-radius: 5px;"></div>"""

    df_with_tooltip = df.copy()
    df_with_tooltip['Topic'] = df_with_tooltip['Topic'].apply(lambda x: f'<a href="http://localhost:8501/#details-for-topic-{x.lower().replace(" ", "-")}">{x}</a>')
    
    return f"{tooltip_script}\n{tooltip_div}\n{df_with_tooltip.to_html(escape=False, index=False)}"

# Function to display circular indicators with two shades
def display_partial_circle_indicator(percentage, color):
    fig, ax = plt.subplots()
    ax.set_aspect('equal')

    # Calculate the starting angle for the percentage
    start_angle = -90  # Starting angle (top position)
    end_angle = start_angle + 360 * percentage / 100  # Calculate the end angle

    ax.add_patch(plt.Circle((0.5, 0.5), 0.4, color=color, alpha=0.5))
    theta = np.linspace(np.radians(start_angle), np.radians(end_angle), 100)
    x = 0.5 + 0.4 * np.cos(theta)
    y = 0.5 + 0.4 * np.sin(theta)
    ax.plot(x, y, color=color, linewidth=20)  # Adjust line width as needed
    ax.text(0.5, 0.5, f"{percentage}%", ha='center', va='center', fontsize=24)
    ax.set_axis_off()
    return fig

# Function to display assessment component for "conviction_score" with circular indicator
def display_conviction_score_component(title, metric_value, metric_text, feedback, color):
    with st.container():
        st.subheader(title)
        col1, col2 = st.columns([1, 4])
        with col1:
            # Display partial circular indicator with two shades
            fig = display_partial_circle_indicator(int(metric_value), color)
            st.pyplot(fig)
        with col2:
            st.text(f"Summary: Dummy summary for 2-3 lines") 
            st.text(f"Feedback: Dummy feedback for 1-2 lines")
            
# Function to display component with grey box and weightage (in percentage)
def display_component_with_weightage(title, metric_value, metric_text, feedback, color_light, weightage):
    weightage_percentage = weightage * 100
    with st.container():
        st.subheader(title)
        col1, col2 = st.columns([1, 4])
        with col1:
            if title != "Overall Conviction Score":  # Exclude weightage for overall conviction score
                # Display partial circular indicator with two shades
                fig = display_partial_circle_indicator(int(metric_value), color_light)
                st.pyplot(fig)
                st.text(f"Weightage: {weightage_percentage:.2f}%")
            else:
                # Display partial circular indicator without weightage for overall conviction score
                fig = display_partial_circle_indicator(int(metric_value), color_light)
                st.pyplot(fig)
        with col2:
            st.text(f"Assessment: {metric_text}")
            st.write(feedback)


# Function to display assessment component with weightage in percentage
def display_component(title, metric_value, metric_text, feedback, color_light, weightage):
    weightage_percentage = weightage * 100
    with st.container():
        st.subheader(title)
        col1, col2 = st.columns([1, 4])
        with col1:
            if metric_value is not None and isinstance(metric_value, (int, float)):
                # Display partial circular indicator with two shades
                fig = display_partial_circle_indicator(int(metric_value), color_light)
                st.pyplot(fig)
                st.text(f"Weightage: {weightage_percentage:.2f}%")
            else:
                st.write("Metric value not available or not numeric")
        with col2:
            st.text(f"Assessment: {metric_text}")
            st.write(feedback)
            
def calculate_overall_scores(unit_data, folder_path):
    ids = [topic['id'] for topic in unit_data['topic_list']]
    topic_titles = [topic['title'] for topic in unit_data['topic_list']]

    overall_conviction_scores = []
    topic_scores = []
    text_scores = []
    audio_scores = []
    video_scores = []

    for id in ids:
        json_file_path = os.path.join(folder_path, f"{id}.json")
        with open(json_file_path, 'r') as file:
            json_data = json.load(file)

        valid_data = [item for item in json_data if 'id' in item]

        text_score = json_data[-2].get('text_conviction_score')
        audio_score = json_data[-2].get('audio_conviction_score')
        video_score = json_data[-2].get('video_conviction_score')
        topic_score = json_data[-2].get('topic_accuracy_score')

        overall_conviction_scores.append(
            (topic_score * 0.5) + (audio_score * 0.05) + (video_score * 0.075) + (text_score * 0.375)
        )

        topic_scores.append(topic_score)
        text_scores.append(text_score)
        audio_scores.append(audio_score)
        video_scores.append(video_score)

    return {
        'Topic': topic_titles,
        'Overall Conviction Score': overall_conviction_scores,
        'Topic Score': topic_scores,
        'Text Score': text_scores,
        'Audio Score': audio_scores,
        'Video Score': video_scores
    }
    
# Function to generate the hover tooltip for topics
def generate_hover_tooltip(df):
    tooltip_html = df.to_html(escape=False, index=False)
    tooltip_html = tooltip_html.replace('<table border="1" class="dataframe">', '<table class="dataframe" style="text-align:center">')
    return tooltip_html

# Function to generate HTML anchor links for each topic
def generate_topic_links(df):
    links = []
    for index, row in df.iterrows():
        topic = row["Topic"]
        # Replace spaces with hyphens and lowercase the text
        topic_id = re.sub(r'\s+', '-', topic.lower())
        links.append(f'<a href="#details-for-topic-{topic_id}">{topic}</a>')
    return links

# Function to display overall conviction score component with circular indicator
def display_overall_conviction_score(title, metric_value, color):
    with st.container():
        st.subheader(title)
        # Display partial circular indicator with two shades
        fig = display_partial_circle_indicator(int(metric_value), color)
        st.pyplot(fig)


# Set the background color to white
st.markdown(
    """
    <style>
    body {
        background-color: #FFFFFF;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Path to the folder containing JSON files
folder_path = r"report jsons"  # Replace this with your folder path

# Read the unit_id_topics.json file to get the IDs
unit_json_path = os.path.join(folder_path, "unit_id_topics.json")
with open(unit_json_path, 'r') as file:
    unit_data = json.load(file)

# Calculate overall and individual scores
scores = calculate_overall_scores(unit_data, folder_path)

# Create a DataFrame with scores for unit-wise display
df = pd.DataFrame(scores)

# Transpose the DataFrame to make columns the topics and scores the rows
df_transposed = df.set_index('Topic').T

# Set the background color to white
st.markdown(
    """
    <style>
    body {
        background-color: #FFFFFF;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Define component weightages and colors
component_weightages = {
    'audio_conviction_score': 0.05,
    'video_conviction_score': 0.075,
    'text_conviction_score': 0.375,
    'topic_accuracy_score': 0.5
}

colors = ['orange', 'yellow', 'purple', 'green', 'blue']

# Sidebar for topic selection
st.sidebar.title('Select Topic')
selected_topic = st.sidebar.selectbox('Choose a topic', ['Unit-wise Scores'] + df['Topic'].tolist())

# Display the selected content based on the topic selection
if selected_topic == 'Unit-wise Scores':
    st.header("Unit-wise Scores")
    # Display the unit-wise scores table
    st.dataframe(df, hide_index=True)
    # st.dataframe(df)
    
    # Add empty line or markdown for spacing
    st.markdown("---")  # You can try using multiple dashes or other markdown to create space

    # Display bar graph for overall conviction scores in a separate section
    st.subheader("Overall Conviction Graph")
    fig, ax = plt.subplots()
    df_transposed.plot(kind='bar', ax=ax, color=['orange', 'yellow', 'purple', 'green', 'blue'], legend=None)
    ax.set_xlabel('Scores')
    ax.set_ylabel('Overall Conviction Score')
    ax.set_xticklabels(df_transposed.index, rotation=45)
    st.pyplot(fig)

else:
    # Extract topic details for the selected topic
    topic_details = df[df['Topic'] == selected_topic]

    # Display details for the selected topic
    st.header(f"Details for topic: {selected_topic}")

    # Extract the ID for the selected topic
    selected_topic_id = None
    for topic in unit_data['topic_list']:
        if topic['title'] == selected_topic:
            selected_topic_id = topic['id']
            break

    if selected_topic_id is not None:
        # Path to individual JSON file based on the selected topic ID
        json_file_path = os.path.join(folder_path, f"{selected_topic_id}.json")
        # Read JSON data from the file
        with open(json_file_path, 'r') as file:
            json_data = json.load(file)

        # Extracting specific data from the JSON file for display
        text_score = json_data[-2].get('text_conviction_score')
        audio_score = json_data[-2].get('audio_conviction_score')
        video_score = json_data[-2].get('video_conviction_score')
        topic_score = json_data[-2].get('topic_accuracy_score')

        # Overall Conviction Score Calculation
        overall_conviction_score = (
            (topic_score * 0.5)
            + (audio_score * 0.05)
            + (video_score * 0.075)
            + (text_score * 0.375)
        )
        
        # Display overall conviction score component with circular indicator
        display_component_with_weightage(
            "Overall Conviction Score",
            overall_conviction_score,
            "Good",
            "The overall assessment indicates a strong command of the topic, but a slight improvement in the video aspect could enhance engagement.",
            colors[4],  # Use a different color for the overall conviction score indicator
            component_weightages['topic_accuracy_score']  # Use the corresponding weightage for this component
        )
        # Display assessment components with circular indicators for the selected topic
        display_component(
            "Topic Accuracy Score",
            topic_score,
            "Good",
            "The assessment notes confident body language and well-designed visuals, suggesting incorporating more pauses for audience comprehension.",
            colors[0],
            component_weightages['topic_accuracy_score']  # Use the corresponding weightage for this component
        )

        display_component(
            "Text Assessment",
            text_score,
            "Good",
            "Below the metric, a short paragraph summarizes the assessment feedback, highlighting strengths like appropriate word choice and confident expression.",
            colors[3],
            component_weightages['text_conviction_score']  # Use the corresponding weightage for this component
        )

        display_component(
            "Audio Assessment",
            audio_score,
            "Great",
            "The assessment feedback highlights clear pronunciation and engaging delivery, with minor suggestions for a slightly slower pace.",
            colors[1],
            component_weightages['audio_conviction_score']  # Use the corresponding weightage for this component
        )

        display_component(
            "Video Assessment",
            video_score,
            "Good",
            "The assessment notes confident body language and well-designed visuals, suggesting incorporating more pauses for audience comprehension.",
            colors[2],
            component_weightages['video_conviction_score']  # Use the corresponding weightage for this component
        )