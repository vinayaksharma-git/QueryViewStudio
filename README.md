# 🔎 Query View Studio

**Query View Studio** is an interactive, low-code data exploration and dashboarding application built with **Streamlit**, **DuckDB**, **Pandas**, and **Plotly**. It provides a split-screen workspace featuring a flexible notebook editor on the left and a live dashboard canvas on the right.


## 🤖 Built with AI

**Query View Studio** was designed and developed with the assistance of **AI**. By leveraging AI-assisted coding and rapid prototyping techniques, the application brings complex data exploration workflows—like DuckDB execution, dynamic Plotly rendering, multi-value filter logic, and state-managed project bundling—into a seamless, user-friendly interface.


## ✨ Features

* 🗂️ **Interactive Split-Screen Layout**
* **Resizable Sidebar:** Dynamically expand or collapse the sidebar. When collapsed, the main workspace auto-expands to fill 100% of the screen.
* **Dual-Pane Canvas:** Keep your code/filters on the left (Notebook Editor) and instantly visualize results on the right (Dashboard Canvas).


* 📊 **Multi-Engine Querying & Views**
* **SQL Cells:** Run fast SQL queries directly against loaded DataFrames using **DuckDB**.
* **Pandas Cells:** Execute Python code snippets for custom data transformations.
* **Power BI / Excel Views:** Low-code, visual builder with drop-down field selectors and **multi-value filtering** (`IN` logic) with zero code required.
* **Markdown Cells:** Document insights, add headings, or structure your report layout.


* 📈 **Dynamic Plotly Visualizations**
* Effortlessly render Tables, Bar Charts, Line Charts, Scatter Plots, Pie Charts, and Area Charts.


* 📦 **Project Bundling**
* Save and load your entire workspace (datasets + query configurations + filters) in a single `.zip` file for seamless project portability.




## 🚀 Quick Start

### 1. Prerequisites

Ensure you have Python 3.8+ installed.

### 2. Installation

Clone the repository and install the required dependencies:

```bash
# Clone the repository
https://github.com/vinayaksharma-git/QueryViewStudio
cd QueryViewStudio

# Install dependencies
pip install streamlit pandas duckdb plotly openpyxl

```

### 3. Running the App

Launch the Streamlit application:

```bash
streamlit run app.py

```


## 🛠️ How to Use

1. **Load Data:** Use the sidebar to upload a dataset (`.csv`, `.xlsx`, or `.json`) or load a previously saved `.zip` Project Bundle.
2. **Add Cells:** Click **✚ Insert Cell** from the sidebar to choose between *SQL Query*, *Pandas Query*, *Power BI / Excel View*, or *Markdown*.
3. **Configure & Filter:**
* **Power BI / Excel View:** Pick your X and Y axes, choose from multi-select dropdowns to apply filters, and hit **▶ Run View**.
* **SQL / Pandas:** Write custom transformations and choose your desired output visual style.


4. **View Outputs:** All outputs render automatically as interactive Plotly charts or data tables on the **Right Panel Dashboard Canvas**.
5. **Save Project:** Click **⎙ Save Project Bundle** in the sidebar to export your session for future use.


## 🧰 Tech Stack

* **Frontend / Framework:** [Streamlit](https://streamlit.io/)
* **Data Processing:** [Pandas](https://pandas.pydata.org/) & [DuckDB](https://duckdb.org/)
* **Data Visualization:** [Plotly Express](https://plotly.com/python/plotly-express/)
