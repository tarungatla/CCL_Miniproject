import streamlit as st
import uuid
from database.dynamodb_operations import DynamoDBOperations
from storage.s3_operations import S3Operations
from config.aws_config import S3_CONFIG

def show_inventory_form():
    db = DynamoDBOperations()
    s3 = S3Operations()
    
    st.subheader("Add/Edit Inventory Item")
    
    # Get existing categories for dropdown
    items = db.get_items()
    existing_categories = sorted(list(set(item['Category'] for item in items)))
    
    with st.form("inventory_form"):
        name = st.text_input("Item Name")
        
        # Category input with option to add new category
        category_option = st.radio("Category", ["Select Existing", "Add New"])
        if category_option == "Select Existing" and existing_categories:
            category = st.selectbox("Select Category", existing_categories)
        else:
            category = st.text_input("Enter Category")
            
        col1, col2 = st.columns(2)
        with col1:
            quantity = st.number_input("Quantity", min_value=0)
        with col2:
            price = st.number_input("Price", min_value=0)
            
        image = st.file_uploader("Upload Image", type=S3_CONFIG['allowed_extensions'])
        
        submit = st.form_submit_button("Add Item")
        
        if submit:
            if name and category and quantity >= 0 and price >= 0:
                try:
                    image_url = ""
                    if image:
                        file_extension = image.name.split('.')[-1]
                        file_name = f"{uuid.uuid4()}.{file_extension}"
                        image_url = s3.upload_file(image, file_name)
                    
                    item_id = db.add_item(name, category, quantity, price, image_url)
                    st.success(f"Item '{name}' added successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error adding item: {str(e)}")
            else:
                st.error("Please fill in all required fields")
    
    # Edit/Delete existing items
    st.subheader("Edit Existing Items")
    for item in items:
        with st.expander(f"{item['Name']} ({item['Category']})"):
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                if item['ImageURL']:
                    st.image(item['ImageURL'], width=100)
                st.write(f"Quantity: {item['Quantity']}")
                st.write(f"Price: ₹{item['Price']:.2f}")
            
            with col2:
                if st.button("Edit", key=f"edit_{item['ItemID']}"):
                    st.session_state.editing_item = item
                    
            with col3:
                if st.button("Delete", key=f"delete_{item['ItemID']}"):
                    try:
                        if item['ImageURL']:
                            file_name = item['ImageURL'].split('/')[-1]
                            s3.delete_file(file_name)
                        db.delete_item(item['ItemID'])
                        st.success(f"Item '{item['Name']}' deleted successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error deleting item: {str(e)}") 