import pandas as pd
def create_category_mapping(df):
    state_categories=(
        df["state_id"].astype("category").cat.categories
    )
    store_categories=(
        df["store_id"]
        .astype("category")
        .cat.categories
    )
    item_categories=(
        df["item_id"]
        .astype("category")
        .cat.categories
    )
    return {
        "state":{
            value:i for i,value in enumerate(state_categories)
        },
        "store":{
            value:i for i,value in enumerate(store_categories)
        },
        "item":{
            value:i for i,value in enumerate(item_categories)
        },
    }
def encode_features(df):
    df = df.copy()

    df["state_encoded"] = (
        df["state_id"]
        .astype("category")
        .cat.codes
    )

    df["store_encoded"] = (
        df["store_id"]
        .astype("category")
        .cat.codes
    )

    df["item_encoded"] = (
        df["item_id"]
        .astype("category")
        .cat.codes
    )

    return df