import streamlit as st
import uuid
from decimal import Decimal
from database.dynamodb_operations import DynamoDBOperations
from storage.s3_operations import S3Operations
from config.aws_config import S3_CONFIG

def convert_decimal(value):
    """Convert Decimal to int or float"""
    if isinstance(value, Decimal):
        return int(value) if value % 1 == 0 else float(value)
    return value

def show_edit_form(item, db, s3):
    """Show form for editing an existing item"""
    with st.form(f"edit_form_{item['ItemID']}"):
        st.subheader(f"Edit Item: {item['Name']}")
        
        # Pre-fill form with existing values
        name = st.text_input("Item Name", value=item['Name'])
        category = st.text_input("Category", value=item['Category'])
        
        col1, col2 = st.columns(2)
        with col1:
            # Convert Decimal to int for quantity
            current_quantity = convert_decimal(item['Quantity'])
            quantity = st.number_input("Quantity", 
                                     min_value=0, 
                                     value=current_quantity)
        with col2:
            # Convert Decimal to float for price
            current_price = convert_decimal(item['Price'])
            # Ensure current_price is a float
            current_price = float(current_price)
            price = st.number_input("Price", 
                                min_value=0.0, 
                                value=current_price,
                                format="%.2f")
                
        # Show current image if it exists
        if item.get('ImageURL'):
            st.image(item['ImageURL'], width=100, caption="Current Image")
        
        # Option to upload new image
        new_image = st.file_uploader("Upload New Image (leave empty to keep current)", 
                                   type=S3_CONFIG['allowed_extensions'])
        
        update_button = st.form_submit_button("Update Item")
        
        if update_button:
            try:
                # Handle image update
                image_url = item.get('ImageURL', '')
                if new_image:
                    # Delete old image if it exists
                    if item.get('ImageURL'):
                        old_file_name = item['ImageURL'].split('/')[-1]
                        s3.delete_file(old_file_name)
                    
                    # Upload new image
                    file_extension = new_image.name.split('.')[-1]
                    file_name = f"{uuid.uuid4()}.{file_extension}"
                    image_url = s3.upload_file(new_image, file_name)
                
                # Update item in DynamoDB
                updates = {
                    'Name': name,
                    'Category': category,
                    'Quantity': quantity,
                    'Price': price,
                    'ImageURL': image_url,
                    'UserEmail': st.session_state.user_email  # Preserve the user email
                }
                
                db.update_item(item['ItemID'], updates)
                st.success("Item updated successfully!")
                # Clear the editing state
                del st.session_state.editing_item
                st.rerun()
            
            except Exception as e:
                st.error(f"Error updating item: {str(e)}")

def show_inventory_form():
    db = DynamoDBOperations()
    s3 = S3Operations()
    
    # Check if we're in edit mode
    editing_item = st.session_state.get('editing_item')
    if editing_item:
        show_edit_form(editing_item, db, s3)
        if st.button("Cancel Edit"):
            del st.session_state.editing_item
            st.rerun()
        return

    st.subheader("Add/Edit Inventory Item")
    
    # Get existing categories for current user's items
    items = db.get_items(user_email=st.session_state.user_email)
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
                    
                    # Add user email when creating item
                    item_id = db.add_item(
                        name=name,
                        category=category,
                        quantity=quantity,
                        price=price,
                        image_url=image_url,
                        user_email=st.session_state.user_email  # Add user email
                    )
                    st.success(f"Item '{name}' added successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error adding item: {str(e)}")
            else:
                st.error("Please fill in all required fields")
    
    # Edit/Delete existing items (only show user's items)
    st.subheader("Edit Existing Items")
    for item in items:  # This now only contains the current user's items
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