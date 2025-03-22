import streamlit as st
import pandas as pd
import plotly.express as px
from database.dynamodb_operations import DynamoDBOperations
from datetime import datetime
import pytz

def convert_to_ist(utc_timestamp):
    """Convert UTC timestamp to IST"""
    try:
        # Parse the UTC timestamp
        utc_dt = datetime.fromisoformat(utc_timestamp.replace('Z', '+00:00'))
        # Convert to IST
        ist = pytz.timezone('Asia/Kolkata')
        ist_dt = utc_dt.astimezone(ist)
        # Format the datetime
        return ist_dt.strftime("%Y-%m-%d %I:%M:%S %p IST")
    except Exception as e:
        return utc_timestamp  # Return original if conversion fails


def show_inventory_view():
    db = DynamoDBOperations()
    items = db.get_items()
    
    # Convert items to DataFrame for easier manipulation
    df = pd.DataFrame(items)
    
    # Ensure ImageURL is treated as a string
    if 'ImageURL' in df.columns:
        df['ImageURL'] = df['ImageURL'].astype(str)
    
    st.subheader("Inventory Overview")
    
    # Filters
    selected_category = []
    min_quantity = 0
    
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
    
    # Modified Detailed inventory table section
    st.subheader("Inventory Details")
    if not filtered_df.empty:
        # Create tabs for different view types
        view_type = st.radio("View Type", ["Table View", "Card View"])
        
        if view_type == "Table View":
            # Create a custom table with images
            for idx, item in filtered_df.iterrows():
                with st.container():
                    cols = st.columns([1, 3, 2, 1, 1])
                    
                    # Display image in first column if available
                    with cols[0]:
                        image_url = item.get('ImageURL')
                        print(image_url)
                        if image_url and image_url != "0" and image_url != "":
                            try:
                                st.image(image_url, width=50)
                            except Exception as e:
                                st.write("Image error")
                        else:
                            st.write("No image")
                    
                    # Display other item details
                    with cols[1]:
                        st.write(f"**{item['Name']}**")
                    with cols[2]:
                        st.write(item['Category'])
                    with cols[3]:
                        st.write(f"{item['Quantity']}")
                    with cols[4]:
                        st.write(f"₹{item['Price']:.2f}")
                    
                    st.divider()
        else:
            # Card view with images
            cols = st.columns(3)
            for idx, item in filtered_df.iterrows():
                with cols[idx % 3]:
                    with st.expander(f"{item['Name']} ({item['Category']})"):
                        image_url = item.get('ImageURL')
                        if image_url and image_url != "0" and image_url != "":
                            try:
                                st.image(image_url, width=200)
                            except Exception as e:
                                st.info("Unable to display image")
                        else:
                            st.info("No image available")
                        
                        st.write("**Details:**")
                        st.write(f"• Category: {item['Category']}")
                        st.write(f"• Quantity: {item['Quantity']}")
                        st.write(f"• Price: ₹{item['Price']:.2f}")
                        st.write(f"• Last Updated: {convert_to_ist(item['Timestamp'])}")
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