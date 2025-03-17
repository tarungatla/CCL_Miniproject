import streamlit as st
import pandas as pd
import plotly.express as px
from database.dynamodb_operations import DynamoDBOperations

def show_inventory_view():
    db = DynamoDBOperations()
    items = db.get_items()
    
    # Convert items to DataFrame for easier manipulation
    df = pd.DataFrame(items)
    
    st.subheader("Inventory Overview")
    
    # Filters
    col1, col2 = st.columns(2)
    with col1:
        if not df.empty and 'Category' in df.columns:
            selected_category = st.multiselect(
                "Filter by Category",
                options=sorted(df['Category'].unique())
            )
    
    with col2:
        if not df.empty:
            min_quantity = st.number_input(
                "Minimum Quantity",
                min_value=0,
                value=0
            )
    
    # Apply filters
    filtered_df = df.copy()
    if selected_category:
        filtered_df = filtered_df[filtered_df['Category'].isin(selected_category)]
    if min_quantity > 0:
        filtered_df = filtered_df[filtered_df['Quantity'] >= min_quantity]
    
    # Display inventory statistics
    st.subheader("Inventory Statistics")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Items", len(filtered_df))
    with col2:
        st.metric("Total Categories", len(filtered_df['Category'].unique()))
    with col3:
        st.metric("Low Stock Items", len(filtered_df[filtered_df['Quantity'] <= 10]))
    
    # Visualizations
    st.subheader("Inventory Analysis")
    
    tab1, tab2 = st.tabs(["Category Distribution", "Stock Levels"])
    
    with tab1:
        if not filtered_df.empty:
            category_counts = filtered_df['Category'].value_counts()
            fig = px.pie(
                values=category_counts.values,
                names=category_counts.index,
                title="Items by Category"
            )
            st.plotly_chart(fig)
    
    with tab2:
        if not filtered_df.empty:
            fig = px.bar(
                filtered_df,
                x='Name',
                y='Quantity',
                color='Category',
                title="Stock Levels by Item"
            )
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig)
    
    # Detailed inventory table
    st.subheader("Inventory Details")
    if not filtered_df.empty:
        # Reorder columns for display
        display_columns = ['Name', 'Category', 'Quantity', 'Price', 'Timestamp']
        display_df = filtered_df[display_columns].copy()
        display_df['Price'] = display_df['Price'].map('₹{:,.2f}'.format)
        
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No items match the selected filters.")
    
    # Export functionality
    if not filtered_df.empty:
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="Export to CSV",
            data=csv,
            file_name="inventory_export.csv",
            mime="text/csv"
        ) 