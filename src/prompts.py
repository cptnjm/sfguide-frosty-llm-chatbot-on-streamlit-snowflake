import streamlit as st

SCHEMA_PATH = st.secrets.get("SCHEMA_PATH", "SANDBOX.JMAUGHAN")
QUALIFIED_TABLE_NAME = f"{SCHEMA_PATH}.DOWNLINE_ADV"
TABLE_DESCRIPTION = """
This table has various metrics for brand partner (Distributors).
The user may describe the entities interchangeably as Brand Patner, customer or distributor intercangabley.
"""
# This query is optional if running Frosty on your own table, especially a wide table.
# Since this is a deep table, it's useful to tell Frosty what variables are available.
# Similarly, if you have a table with semi-structured data (like JSON), it could be used to provide hints on available keys.
# If altering, you may also need to modify the formatting logic in get_table_context() below.
METADATA_QUERY = f"SELECT RFM_Segment_name as VARIABLE_NAME,RFM_SEGMENT_DESCRIPTION as DEFINITION FROM {SCHEMA_PATH}.definitions;"

GEN_SQL = """
You will be acting as an AI Snowflake SQL and commentarty Expert named Frosty.
Your goal is to give recommendations on running their YOUNG LIVING, MLM distributor business or  give correct, executable sql query to users.
You will be replying to users who will be confused if you don't respond in the character of Frosty.
You are given two tables, the table names are in <tableName> tag, the columns are in <columns> tag.
The user will ask questions, for each question you should respond and may include a sql query based on the question, the table and commentary. With helpful tips. 
Give query preferences to Using the RFM model found in RFM_SEGMENT_NAME RFM_SEGMENT_DESCRIPTION ,t.ACTIONABLE_TIP
There is no need to be sorry when responding to changes in questions
{context}

Here are 6 critical rules for the interaction you must abide:
<rules>
1. You MUST MUST wrap the generated sql code within ``` sql code markdown in this format e.g
```sql
(select 1) union (select 2)
```
2. If I don't tell you to find a limited set of results in the sql query or question, you MUST limit the number of responses to 10.
3. Text / string where clauses must be fuzzy match e.g ilike %keyword%
4. Make sure to generate a single snowflake sql code, not multiple. 
5. You should only use the table columns given in <columns>, and the table given in <tableName>, you MUST NOT hallucinate about the table names
6. DO NOT put numerical at the very front of sql variable.
7. If I don't tell you to find a limited set of results in the sql query or question, you MUST limit the number of responses to 10
8. Always provide commentary and tips.
</rules>

Don't forget to use "ilike %keyword%" for fuzzy match queries (especially for variable_name column)
and wrap the generated sql code with ``` sql code markdown in this format e.g:
```sql
(select 1) union (select 2)
```
Don't forget rule 2 and 7. 

For each question from the user, make sure to include a query in your response. Unless the response can be answered without a query.

If the user has any questions about their downline use the following for actionable items or rfm descriptions, these can also be used to see potential or where a customer buying habits lay, these are all found in <tablename> the are formated as RFM_SEGMENT_ID	RFM_SEGMENT_NAME	RFM_SEGMENT_DESCRIPTION	ACTIONABLE_TIP
1	Champions	Bought recently, buy often and spend the most	Reward them. Can be Early adopters for New Products. Will promote YL.
2	Loyal Customers	Spend good money. Responsive to promotions	Upsell higher value products. Ask for reviews. Engage them.
3	Potential Loyalist	Recent customers, but spent a good amount and bought more than once	Offer loyalty program, recommend other products
4	Recent Customers	Bought more recently, but not often	Provide on-boarding support, give them early success, start building relationship
5	Promising	Recent shoppers, but have not spent much	Create brand awareness, offer free trials
6	Need Attention	Above average recency, frequency & monetary values	Make limited time offers, Recommend based on past purchases. Reactivate them.
7	About To Sleep	Below average recency, frequency & monetary values	Share valuable resources, recommend popular products at a discount, reconnect with them.
8	At Risk	Spent big money, purchased often but a long time ago	Send personalized emails to reconnect, offer loyalty benefits, provide helpful resources.
9	Cannot Lose Them	Made big purchases and often, but a long time ago	Win them back via loyalty programs or newer products, don’t lose them to competition, talk to them.
10	Hibernating	Last purchase was long ago, low spenders and bought seldomly	Offer other relevant products and special discounts. Recreate brand value.
11	Lost	Lowest recency, frequency & monetary scores	Revive interest with reach out campaign, ignore otherwise.
12	Other	Does not fit within a segment	Will fit within another category in the future
0	SR Star+	Commissionable Sr Star and above. Those that are building the business.	Nothing

Now to get started, please very briefly introduce yourself and share the available metrics in 1-3 sentences.
Then provide 3 example questions using bullet points.
"""

@st.cache_data(show_spinner="Loading Frosty's context...")
def get_table_context(table_name: str, table_description: str, metadata_query: str = None):
    table = table_name.split(".")
    conn = st.connection("snowflake")
    columns = conn.query(f"""
        SELECT COLUMN_NAME, DATA_TYPE FROM {table[0].upper()}.INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = '{table[1].upper()}' AND TABLE_NAME = '{table[2].upper()}'
        """, show_spinner=False,
    )
    columns = "\n".join(
        [
            f"- **{columns['COLUMN_NAME'][i]}**: {columns['DATA_TYPE'][i]}"
            for i in range(len(columns["COLUMN_NAME"]))
        ]
    )
    context = f"""
Here is the table name <tableName> {'.'.join(table)} </tableName>

<tableDescription>{table_description}</tableDescription>

Here are the columns of the {'.'.join(table)}

<columns>\n\n{columns}\n\n</columns>
    """
    context = context + f"""
There is an additional table named <tablename>SANDBOX.JMAUGHAN.fact_order_lines</tablename> with the following table description:
<tableDescription>It contains all order and order line informaiton for all orders from the downline of the user.</tableDescription>

Here are the columns of the SANDBOX.JMAUGHAN.fact_order_lines table:
<columns>
FACT_ORDER_LINE_SK, ORDER_LINE_ITEM_ID, ORDER_ID, ORIGINAL_ORDER_ID, DIM_EXCHANGE_RATE_SK, DIM_MEMBER_SK, CUST_ID, DIM_WAREHOUSE_SK, DIM_ORDERING_WAREHOUSE_SK, DIM_ORDER_SOURCE_SK, DIM_ORDER_TYPE_SK, DIM_CURRENCY_SK, DIM_PRICE_TYPE_SK, DIM_ORDER_ATTRIBUTE_SK, DIM_SHIPPING_GEOGRAPHY_SK, DIM_SHIPPING_ADDRESS_SK, DIM_MEMBER_MAIN_EXCHANGE_RATE_GEOGRAPHY_SK, DIM_WAREHOUSE_EXCHANGE_RATE_GEOGRAPHY_SK, DIM_PRODUCT_SK, DIM_AGENT_SK, SHIPMENT_ID, ORDER_LINE_WAREHOUSE_ID, DIM_ORDER_LINE_WAREHOUSE_SK, DIM_SHIPPING_METHOD_SK, ORDER_ENTERED_DATE, ORDER_ENTERED_DATE_ID, ORDER_PAID_DATE, ORDER_PAID_DATE_ID, ORDER_COMMISSION_DATE, ORDER_COMMISSION_DATE_ID, TAX_JOURNAL_DATE, TAX_JOURNAL_DATE_ID, PACKING_SLIP_CREATED_DATE, PACKING_SLIP_CREATED_DATE_ID, SHIPPED_DATE, SHIPPED_DATE_ID, DELIVERED_ESTIMATE_DAYS_TO_ADD_DATE, DELIVERED_ESTIMATE_DTTM, DELIVERED_ESTIMATE_DATE_ID, RELEASED_DATE, RELEASED_DATE_ID, SHIPPED_SLA_DATE, SHIPPED_SLA_DATE_ID, PRODUCT_QUANTITY, DISCOUNT_PERCENT, PRODUCT_SALES_PRICE_USD, PRODUCT_SALES_PRICE_LOCAL, PRODUCT_SALES_AMOUNT_USD, PRODUCT_SALES_AMOUNT_LOCAL, TAXABLE_SALES_AMOUNT_USD, TAXABLE_SALES_AMOUNT_LOCAL, TAX_SALES_PERCENT, TAX_SALES_AMOUNT_USD, TAX_SALES_AMOUNT_LOCAL, SHIPPING_WEIGHT_POUNDS, SHIPPING_WEIGHT_KILOGRAMS, PRODUCT_PV_AMOUNT, PV_AMOUNT, PRODUCT_POINTS_AMOUNT, POINTS_AMOUNT, PRODUCT_COST_AMOUNT_LOCAL, PRODUCT_COST_AMOUNT_USD, EXTENDED_PRODUCT_COST_AMOUNT_LOCAL, EXTENDED_PRODUCT_COST_AMOUNT_USD, OTHER_PRICE_2, DW_INSERT_DTTM, DW_UPDATE_DTTM, SRC_UPDATE_DATE, DW_DELETE_DTTM, DW_DELETED_FLAG, DIM_DATE_ID, DATE_SHORT_NAME, DATE_SHORT, DATE_SHORT_INTERNATIONAL, DATE_INTERNATIONAL, DATE_LONG_NAME, DAY_OF_WEEK_NUMBER, DAY_OF_WEEK_NAME, DAY_OF_MONTH, DAY_OF_YEAR, MONTH_NUMBER, MONTH_LONG_NAME, MONTH_SHORT_NAME, QUARTER_LONGNAME, QUARTER_NUMBER, QUARTER_SHORT_NAME, WEEK_NUMBER, WEEK_BEGIN_DATE, WORK_WEEK_BEGIN_DATE, WEEK_END_DATE, YEAR_NUMBER, COMMISSION_PERIOD_ID, WEEKEND_FLAG, HOLIDAY_FLAG, FDM_DATE_ID, FISCAL_QTR, LAST_DAY_MNTH_FLAG, DAYS_IN_MONTH, QTR_YEAR, PREVIOUS_DAY, TRAILING_7_DAYS, TRAILING_14_DAYS, TRAILING_8_TO_21_DAYS, TRAILING_30_DAYS, TRAILING_60_DAYS, TRAILING_90_DAYS, TRAILING_180_DAYS, TRAILING_365_DAYS, TRAILING_1_MONTH, TRAILING_3_MONTHS, TRAILING_6_MONTHS, TRAILING_9_MONTHS, TRAILING_12_MONTHS, TRAILING_24_MONTHS, CURRENT_MONTH_TO_DATE, DAYS_AGO, MONTHS_AGO, YEARS_AGO, HALF_YEAR_FLAG, DATE_JULIAN, MONTH_BEGIN_DATE, MONTH_END_DATE
</columns>
use 
Cust_id is the primary indentifier for any single member
    """

    if metadata_query:
        metadata = conn.query(metadata_query, show_spinner=False)
        metadata = "\n".join(
            [
                f"- **{metadata['VARIABLE_NAME'][i]}**: {metadata['DEFINITION'][i]}"
                for i in range(len(metadata["VARIABLE_NAME"]))
            ]
        )
        context = context + f"\n\nAvailable variables by VARIABLE_NAME:\n\n{metadata}" 
    return context





def get_system_prompt():
    table_context = get_table_context(
        table_name=QUALIFIED_TABLE_NAME,
        table_description=TABLE_DESCRIPTION,
       
    )
    return GEN_SQL.format(context=table_context)

# do `streamlit run prompts.py` to view the initial system prompt in a Streamlit app
if __name__ == "__main__":
    st.header("System prompt for Frosty")
    st.markdown(get_system_prompt())
