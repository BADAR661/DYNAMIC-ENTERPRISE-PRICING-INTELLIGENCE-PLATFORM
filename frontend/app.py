import os
import requests
import streamlit as st
import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

try:
    configured_api_url = st.secrets.get("API_BASE_URL")
except Exception:
    configured_api_url = None

API_BASE_URL = configured_api_url or os.getenv(
    "API_BASE_URL",
    "http://127.0.0.1:8000",
)


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Enterprise Dynamic Pricing Intelligence",
    page_icon="💹",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# CUSTOM STYLING
# ============================================================

st.markdown(
    """
    <style>

    .main {
        background-color: #f8fafc;
    }

    .block-container {
        max-width: 1500px;
        padding-top: 1.5rem;
        padding-bottom: 3rem;
    }

    .hero {
        background: linear-gradient(
            135deg,
            #111827,
            #1f2937
        );
        padding: 2rem;
        border-radius: 18px;
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 30px rgba(0,0,0,0.08);
    }

    .hero-title {
        color: white;
        font-size: 2.4rem;
        font-weight: 800;
    }

    .hero-subtitle {
        color: #d1d5db;
        margin-top: 0.4rem;
        font-size: 1rem;
    }

    .card {
        background: white;
        padding: 1.25rem;
        border-radius: 15px;
        border: 1px solid #e5e7eb;
        box-shadow: 0 3px 12px rgba(0,0,0,0.04);
    }

    .card-title {
        color: #6b7280;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .card-value {
        color: #111827;
        font-size: 1.65rem;
        font-weight: 800;
        margin-top: 0.25rem;
    }

    .card-subtitle {
        color: #9ca3af;
        font-size: 0.78rem;
        margin-top: 0.25rem;
    }

    .section {
        margin-top: 1.5rem;
        margin-bottom: 0.75rem;
    }

    .footer {
        text-align: center;
        color: #9ca3af;
        padding-top: 3rem;
        padding-bottom: 1rem;
    }

    [data-testid="stSidebar"] {
        background-color: #111827;
    }

    [data-testid="stSidebar"] * {
        color: white;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# API HELPERS
# ============================================================

def get_api(endpoint: str):
    try:
        response = requests.get(
            f"{API_BASE_URL}{endpoint}",
            timeout=15,
        )

        if response.status_code == 200:
            return True, response.json()

        try:
            error = response.json()
        except Exception:
            error = response.text

        return False, {
            "status_code": response.status_code,
            "error": error,
        }

    except requests.exceptions.ConnectionError:
        return False, {
            "error": "FastAPI backend is not running."
        }

    except requests.exceptions.Timeout:
        return False, {
            "error": "Backend request timed out."
        }

    except Exception as error:
        return False, {
            "error": str(error)
        }


def post_api(endpoint: str, payload: dict):
    try:
        response = requests.post(
            f"{API_BASE_URL}{endpoint}",
            json=payload,
            timeout=90,
        )

        if response.status_code in (200, 201):
            return True, response.json()

        try:
            error = response.json()
        except Exception:
            error = response.text

        return False, {
            "status_code": response.status_code,
            "error": error,
        }

    except requests.exceptions.ConnectionError:
        return False, {
            "error": "FastAPI backend is not running."
        }

    except requests.exceptions.Timeout:
        return False, {
            "error": "Backend request timed out."
        }

    except Exception as error:
        return False, {
            "error": str(error)
        }


def get_products():
    success, result = get_api("/products")

    if success and result.get("status") == "success":
        return result.get("products", [])

    return []


# ============================================================
# FORMATTERS
# ============================================================

def money(value):
    try:
        if value is None:
            return "N/A"

        return f"${float(value):,.2f}"

    except Exception:
        return "N/A"


def number(value):
    try:
        if value is None:
            return "N/A"

        return f"{float(value):,.2f}"

    except Exception:
        return "N/A"


def percentage(value):
    try:
        if value is None:
            return "N/A"

        return f"{float(value):.2f}%"

    except Exception:
        return "N/A"


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        """
        <div style="text-align:center;padding:20px 0;">

            <div style="font-size:3rem;">
                💹
            </div>

            <div style="
                font-size:1.25rem;
                font-weight:800;
            ">
                Dynamic Pricing
            </div>

            <div style="
                font-size:0.75rem;
                color:#9ca3af;
            ">
                Enterprise Intelligence Platform
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    st.markdown("### Navigation")

    page = st.radio(
        "Navigation",
        [
            "📊 Executive Dashboard",
            "💰 Pricing Optimization",
            "📈 Demand Forecasting",
            "🧠 Explainability",
            "🧮 Revenue Simulation",
            "❤️ System Health",
        ],
        label_visibility="collapsed",
    )

    st.divider()

    api_ok, api_health = get_api("/health")

    if api_ok:
        st.success("API ONLINE")
    else:
        st.error("API OFFLINE")

    st.caption("FastAPI")
    st.caption(API_BASE_URL)


# ============================================================
# EXECUTIVE DASHBOARD
# ============================================================

if page == "📊 Executive Dashboard":

    st.markdown(
        """
        <div class="hero">

            <div class="hero-title">
                Enterprise Dynamic Pricing Intelligence
            </div>

            <div class="hero-subtitle">
                AI-powered demand forecasting, dynamic pricing,
                revenue optimization and explainable ML.
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    success, data = get_api("/dashboard/summary")

    if not success:

        st.error("Unable to load dashboard summary.")
        st.json(data)

    else:

        forecast_status = data.get(
            "forecast_status",
            "READY",
        )

        alert_level = data.get(
            "alert_level",
            "NORMAL",
        )

        action = data.get(
            "recommended_action",
            "No recommendation available.",
        )

        c1, c2, c3, c4 = st.columns(4)

        with c1:
            st.metric(
                "Forecast Engine",
                str(forecast_status).upper(),
            )

        with c2:
            st.metric(
                "Alert Level",
                str(alert_level).upper(),
            )

        with c3:
            st.metric(
                "Pricing Engine",
                "READY",
            )

        with c4:
            st.metric(
                "Explainability",
                "SHAP + LIME",
            )

        st.divider()

        st.subheader("🎯 Recommended Action")

        st.info(action)

        st.subheader("Platform Overview")

        c1, c2, c3 = st.columns(3)

        with c1:
            st.markdown(
                """
                <div class="card">

                <div class="card-title">
                MACHINE LEARNING
                </div>

                <div class="card-value">
                XGBoost
                </div>

                <div class="card-subtitle">
                Demand forecasting model
                </div>

                </div>
                """,
                unsafe_allow_html=True,
            )

        with c2:
            st.markdown(
                """
                <div class="card">

                <div class="card-title">
                PRICING
                </div>

                <div class="card-value">
                Dynamic
                </div>

                <div class="card-subtitle">
                Base • Discount • Peak • Bundle
                </div>

                </div>
                """,
                unsafe_allow_html=True,
            )

        with c3:
            st.markdown(
                """
                <div class="card">

                <div class="card-title">
                EXPLAINABILITY
                </div>

                <div class="card-value">
                SHAP + LIME
                </div>

                <div class="card-subtitle">
                Transparent ML decisions
                </div>

                </div>
                """,
                unsafe_allow_html=True,
            )

        st.subheader("Technology Stack")

        stack = pd.DataFrame(
            [
                ["Backend", "FastAPI", "Online"],
                ["ML Model", "XGBoost", "Ready"],
                ["Database", "SQLite + SQLAlchemy", "Connected"],
                ["Cache", "Redis", "Connected"],
                ["Experiment Tracking", "MLflow", "Integrated"],
                ["Explainability", "SHAP + LIME", "Ready"],
                ["Frontend", "Streamlit", "Running"],
            ],
            columns=[
                "Component",
                "Technology",
                "Status",
            ],
        )

        st.dataframe(
            stack,
            use_container_width=True,
            hide_index=True,
        )


# ============================================================
# PRICING OPTIMIZATION
# ============================================================

elif page == "💰 Pricing Optimization":

    st.title("💰 Dynamic Pricing Optimization")

    st.write(
        "Optimize product prices and immediately evaluate "
        "the expected financial impact."
    )

    st.divider()

    products = get_products()

    with st.form("pricing_form"):

        c1, c2 = st.columns(2)

        with c1:

            if products:
                product_options = {
                    f"{product['product_id']} - {product['name']}":
                        product["product_id"]
                    for product in products
                }

                product_label = st.selectbox(
                    "Product",
                    list(product_options),
                )

                product_id = product_options[product_label]

            else:
                product_id = st.text_input(
                    "Product ID",
                    value="P002",
                    help="Enter an existing product ID.",
                )

            strategy = st.selectbox(
                "Pricing Strategy",
                [
                    "base",
                    "discount",
                    "peak",
                    "bundle",
                ],
            )

            base_price = st.number_input(
                "Base Price",
                min_value=0.01,
                value=1500.0,
                step=10.0,
            )

            expected_quantity = st.number_input(
                "Expected Quantity",
                min_value=0,
                value=10,
                step=1,
            )

            cost_per_unit = st.number_input(
                "Cost Per Unit",
                min_value=0.0,
                value=950.0,
                step=10.0,
            )

        with c2:

            discount = st.number_input(
                "Discount Percentage",
                min_value=0.0,
                max_value=100.0,
                value=10.0,
                step=1.0,
            )

            peak_hour = st.checkbox(
                "Peak Hour"
            )

            peak_multiplier = st.number_input(
                "Peak Multiplier",
                min_value=0.01,
                value=1.10,
                step=0.05,
            )

            bundle_discount = st.number_input(
                "Bundle Discount %",
                min_value=0.0,
                max_value=100.0,
                value=0.0,
                step=1.0,
            )

        bundle_text = st.text_input(
            "Bundle Product Prices",
            placeholder="Example: 500, 700, 900",
        )

        submitted = st.form_submit_button(
            "🚀 Optimize Price",
            use_container_width=True,
        )

    if submitted:

        product_id = product_id.strip()

        if not product_id:
            st.error("Product ID is required.")
            st.stop()

        bundle_prices = None

        if bundle_text.strip():

            try:

                bundle_prices = [
                    float(x.strip())
                    for x in bundle_text.split(",")
                    if x.strip()
                ]

            except ValueError:

                st.error(
                    "Bundle prices must be numeric."
                )

                st.stop()

        payload = {
            "product_id": product_id,
            "pricing_strategy": strategy,
            "base_price": base_price,
            "expected_quantity": int(
                expected_quantity
            ),
            "cost_per_unit": cost_per_unit,
            "discount_percentage": discount,
            "is_peak_hour": peak_hour,
            "peak_multiplier": peak_multiplier,
            "bundle_product_prices": bundle_prices,
            "bundle_discount_percentage": bundle_discount,
        }

        with st.spinner(
            "Running pricing optimization..."
        ):

            success, result = post_api(
                "/pricing/optimize-and-simulate",
                payload,
            )

        if success:

            st.success(
                "Pricing optimization completed successfully."
            )

            c1, c2, c3, c4 = st.columns(4)

            with c1:
                st.metric(
                    "Base Price",
                    money(
                        result.get("base_price")
                    ),
                )

            with c2:
                st.metric(
                    "Optimized Price",
                    money(
                        result.get("optimized_price")
                    ),
                )

            with c3:
                st.metric(
                    "Revenue",
                    money(
                        result.get("expected_revenue")
                    ),
                )

            with c4:
                st.metric(
                    "Profit",
                    money(
                        result.get("expected_profit")
                    ),
                )

            st.divider()

            c1, c2, c3 = st.columns(3)

            with c1:
                st.metric(
                    "Total Cost",
                    money(
                        result.get("total_cost")
                    ),
                )

            with c2:
                st.metric(
                    "Profit Margin",
                    percentage(
                        result.get(
                            "profit_margin_percentage"
                        )
                    ),
                )

            with c3:
                st.metric(
                    "Quantity",
                    number(
                        result.get(
                            "expected_quantity"
                        )
                    ),
                )

            st.subheader("Product Information")

            product_info = {
                "Product ID": result.get(
                    "product_id",
                    product_id,
                ),
                "Product Name": result.get(
                    "product_name",
                    "Not provided by API",
                ),
                "Pricing Strategy": result.get(
                    "pricing_strategy",
                    strategy,
                ),
                "Base Price": money(
                    result.get("base_price")
                ),
                "Optimized Price": money(
                    result.get("optimized_price")
                ),
            }

            st.json(product_info)

            chart_df = pd.DataFrame(
                {
                    "Price Type": [
                        "Base Price",
                        "Optimized Price",
                    ],
                    "Price": [
                        result.get(
                            "base_price",
                            0,
                        ),
                        result.get(
                            "optimized_price",
                            0,
                        ),
                    ],
                }
            )

            st.subheader("Price Comparison")

            st.bar_chart(
                chart_df.set_index(
                    "Price Type"
                )
            )

            st.subheader("Database Integration")

            db_status = {
                "Database Saved": result.get(
                    "database_saved",
                    False,
                ),
                "Recommendation ID": result.get(
                    "recommendation_id",
                    "N/A",
                ),
                "Pricing History ID": result.get(
                    "pricing_history_id",
                    "N/A",
                ),
            }

            st.json(db_status)

            with st.expander(
                "Raw Pricing API Response"
            ):
                st.json(result)

        else:

            st.error(
                "Pricing optimization failed."
            )

            st.json(result)


# ============================================================
# DEMAND FORECASTING
# ============================================================

elif page == "📈 Demand Forecasting":

    st.title("📈 Demand Forecasting")

    st.write(
        "Generate product-specific future demand using the "
        "trained XGBoost forecasting model."
    )

    st.info(
        "The forecast uses the selected Product ID's historical "
        "sales data. Changing the Product ID therefore changes "
        "the model input."
    )

    st.divider()

    products = get_products()

    with st.form("forecast_form"):

        c1, c2 = st.columns(2)

        with c1:

            if products:
                product_options = {
                    f"{product['product_id']} - {product['name']}":
                        product["product_id"]
                    for product in products
                }

                product_label = st.selectbox(
                    "Product",
                    list(product_options),
                )

                product_id = product_options[product_label]

            else:
                product_id = st.text_input(
                    "Product ID",
                    value="P002",
                    help="Example: P001, P002, P003",
                )

            days_ahead = st.slider(
                "Days Ahead",
                1,
                90,
                7,
            )

        with c2:

            st.markdown(
                """
                **Forecasting Mode**

                Product-specific historical data →  
                Feature engineering →  
                XGBoost →  
                Predicted demand
                """
            )

        submitted = st.form_submit_button(
            "🔮 Generate Forecast",
            use_container_width=True,
        )

    if submitted:

        product_id = product_id.strip()

        if not product_id:

            st.error(
                "Product ID is required."
            )

            st.stop()

        params = {
            "product_id": product_id,
            "days_ahead": int(days_ahead),
        }

        with st.spinner(
            "Loading product data and running XGBoost..."
        ):

            try:

                response = requests.post(
                    f"{API_BASE_URL}/predict",
                    params=params,
                    timeout=90,
                )

                if response.status_code == 200:

                    success = True
                    result = response.json()

                else:

                    success = False

                    try:
                        result = response.json()
                    except Exception:
                        result = response.text

            except requests.exceptions.ConnectionError:

                success = False
                result = {
                    "error":
                        "FastAPI backend is not running."
                }

            except requests.exceptions.Timeout:

                success = False
                result = {
                    "error":
                        "Backend request timed out."
                }

            except Exception as error:

                success = False
                result = {
                    "error": str(error)
                }

        if success and result.get("status") == "success":

            if not result.get("product_name"):

                product_success, product_result = get_api(
                    f"/product/{product_id}"
                )

                if product_success:

                    result["product_name"] = product_result.get(
                        "name",
                        "N/A",
                    )

        if success:

            if result.get("status") in [
                "no_data",
                "model_not_trained",
                "data_missing",
            ]:

                st.warning(
                    result.get(
                        "message",
                        "Forecast could not be generated.",
                    )
                )

                st.json(result)

            else:

                st.success(
                    "Forecast generated successfully."
                )

                # ------------------------------------------------
                # PRODUCT INFORMATION
                # ------------------------------------------------

                st.subheader(
                    "📦 Product Information"
                )

                c1, c2 = st.columns(2)

                with c1:

                    st.metric(
                        "Product Name",
                        result.get(
                            "product_name",
                            "N/A",
                        ),
                    )

                with c2:

                    st.metric(
                        "Product ID",
                        result.get(
                            "product_id",
                            product_id,
                        ),
                    )

                c1, c2 = st.columns(2)
                with c1:

                 st.metric(
                    "Forecast Horizon",
                      f"{result.get('days_ahead', days_ahead)} days",
                        )
               

                # ------------------------------------------------
                # MAIN FORECAST RESULT
                # ------------------------------------------------

                st.divider()

                c1, c2, c3 = st.columns(3)

                with c1:

                    st.metric(
                        "Predicted Demand",
                        number(
                            result.get(
                                "predicted_demand"
                            )
                        ),
                    )

                with c2:

                    st.metric(
                        "Forecast Date",
                        result.get(
                            "forecast_date",
                            "N/A",
                        ),
                    )

                with c3:

                    st.metric(
                        "Model",
                        result.get(
                            "source",
                            "XGBoost",
                        ),
                    )

                # ------------------------------------------------
                # PRODUCT-SPECIFIC FEATURES
                # ------------------------------------------------

                st.divider()

                st.subheader(
                    "🔍 Product-Specific Forecast Features"
                )

                features = result.get(
                    "feature_values",
                    {},
                )

                if features:

                    feature_df = pd.DataFrame(
                        [
                            {
                                "Feature": key,
                                "Value": value,
                            }
                            for key, value
                            in features.items()
                        ]
                    )

                    feature_df["Value"] = feature_df[
                        "Value"
                    ].astype(str)

                    st.dataframe(
                        feature_df,
                        use_container_width=True,
                        hide_index=True,
                    )

                else:

                    st.info(
                        "No feature values were returned by the API."
                    )

                # ------------------------------------------------
                # FORECAST SUMMARY
                # ------------------------------------------------

                st.subheader(
                    "📊 Forecast Summary"
                )

                forecast_summary = pd.DataFrame(
                    [
                        [
                            "Product Name",
                            result.get(
                                "product_name",
                                "N/A",
                            ),
                        ],
                        [
                            "Product ID",
                            result.get(
                                "product_id",
                                product_id,
                            ),
                        ],
                        [
                            "Days Ahead",
                            result.get(
                                "days_ahead",
                                days_ahead,
                            ),
                        ],
                        [
                            "Predicted Demand",
                            number(
                                result.get(
                                    "predicted_demand"
                                )
                            ),
                        ],
                        [
                            "Model",
                            result.get(
                                "source",
                                "XGBoost",
                            ),
                        ],
                    ],
                    columns=[
                        "Metric",
                        "Value",
                    ],
                )

                forecast_summary["Value"] = forecast_summary[
                    "Value"
                ].astype(str)

                st.dataframe(
                    forecast_summary,
                    use_container_width=True,
                    hide_index=True,
                )

                with st.expander(
                    "Raw Forecast API Response"
                ):

                    st.json(result)

        else:

            st.error(
                "Forecasting request failed."
            )

            st.json(result)


# ============================================================
# EXPLAINABILITY
# ============================================================

elif page == "🧠 Explainability":

    st.title(
        "🧠 Explainable AI"
    )

    st.write(
        "Understand why the forecasting model produced "
        "its prediction using SHAP and LIME."
    )

    st.info(
        "SHAP provides feature contribution values. "
        "LIME creates a local approximation of the model "
        "around the selected prediction."
    )

    st.divider()

    st.subheader(
        "Forecast Features"
    )

    c1, c2, c3 = st.columns(3)

    with c1:

        previous_sales = st.number_input(
            "Previous Sales",
            min_value=0.0,
            value=2.0,
            step=1.0,
            key="explain_previous_sales",
        )

        lag_7_sales = st.number_input(
            "Lag 7 Sales",
            min_value=0.0,
            value=2.0,
            step=1.0,
            key="explain_lag_7_sales",
        )

        day_of_week = st.number_input(
            "Day of Week",
            min_value=0,
            max_value=6,
            value=1,
            step=1,
            key="explain_day",
        )

        month = st.number_input(
            "Month",
            min_value=1,
            max_value=12,
            value=8,
            step=1,
            key="explain_month",
        )

        is_holiday = st.number_input(
            "Holiday",
            min_value=0,
            max_value=1,
            value=0,
            step=1,
            key="explain_holiday",
        )

    with c2:

        price_trend = st.number_input(
            "Price Trend",
            value=24.39,
            step=0.01,
            key="explain_price_trend",
        )

        recommended_price_trend = st.number_input(
            "Recommended Price Trend",
            value=35.61,
            step=0.01,
            key="explain_recommended_price_trend",
        )

        day_of_week_sin = st.number_input(
            "Day of Week Sin",
            value=0.781831,
            step=0.001,
            format="%.6f",
            key="explain_dow_sin",
        )

        day_of_week_cos = st.number_input(
            "Day of Week Cos",
            value=0.623490,
            step=0.001,
            format="%.6f",
            key="explain_dow_cos",
        )

    with c3:

        month_sin = st.number_input(
            "Month Sin",
            value=-0.866025,
            step=0.001,
            format="%.6f",
            key="explain_month_sin",
        )

        month_cos = st.number_input(
            "Month Cos",
            value=-0.5,
            step=0.001,
            format="%.6f",
            key="explain_month_cos",
        )

        week_of_year_sin = st.number_input(
            "Week of Year Sin",
            value=0.0,
            step=0.001,
            format="%.6f",
            key="explain_week_sin",
        )

        week_of_year_cos = st.number_input(
            "Week of Year Cos",
            value=0.0,
            step=0.001,
            format="%.6f",
            key="explain_week_cos",
        )

    features = {
        "previous_sales": previous_sales,
        "lag_7_sales": lag_7_sales,
        "day_of_week": int(day_of_week),
        "month": int(month),
        "is_holiday": int(is_holiday),
        "price_trend": price_trend,
        "recommended_price_trend": recommended_price_trend,
        "day_of_week_sin": day_of_week_sin,
        "day_of_week_cos": day_of_week_cos,
        "month_sin": month_sin,
        "month_cos": month_cos,
        "week_of_year_sin": week_of_year_sin,
        "week_of_year_cos": week_of_year_cos,
    }

    st.divider()

    c1, c2 = st.columns(2)

    with c1:

        run_shap = st.button(
            "🔍 Explain with SHAP",
            use_container_width=True,
        )

    with c2:

        run_lime = st.button(
            "🔬 Explain with LIME",
            use_container_width=True,
        )

    # ========================================================
    # SHAP
    # ========================================================

    if run_shap:

        with st.spinner(
            "Generating SHAP explanation..."
        ):

            success, result = post_api(
                "/explainability/shap",
                features,
            )

        if success:

            st.success(
                "SHAP explanation generated."
            )

            c1, c2 = st.columns(2)

            with c1:

                st.metric(
                    "Prediction",
                    number(
                        result.get(
                            "prediction"
                        )
                    ),
                )

            with c2:

                st.metric(
                    "Base Value",
                    number(
                        result.get(
                            "base_value"
                        )
                    ),
                )

            shap_features = result.get(
                "features",
                [],
            )

            if shap_features:

                shap_df = pd.DataFrame(
                    shap_features
                )

                if "shap_value" in shap_df.columns:

                    shap_df = shap_df.sort_values(
                        "shap_value"
                    )

                    st.subheader(
                        "SHAP Feature Contributions"
                    )

                    st.bar_chart(
                        shap_df.set_index(
                            "feature"
                        )["shap_value"]
                    )

                st.dataframe(
                    pd.DataFrame(
                        shap_features
                    ),
                    use_container_width=True,
                    hide_index=True,
                )

            with st.expander(
                "Raw SHAP Response"
            ):

                st.json(result)

        else:

            st.error(
                "SHAP explanation failed."
            )

            st.json(result)

    # ========================================================
    # LIME
    # ========================================================

    if run_lime:

        with st.spinner(
            "Generating LIME explanation..."
        ):

            success, result = post_api(
                "/explainability/lime",
                features,
            )

        if success:

            st.success(
                "LIME explanation generated."
            )

            st.metric(
                "Prediction",
                number(
                    result.get(
                        "prediction"
                    )
                ),
            )

            lime_features = result.get(
                "features",
                result.get(
                    "explanation",
                    [],
                ),
            )

            if (
                isinstance(
                    lime_features,
                    list,
                )
                and lime_features
            ):

                lime_rows = []

                for item in lime_features:

                    if isinstance(
                        item,
                        dict,
                    ):

                        lime_rows.append(
                            item
                        )

                    elif (
                        isinstance(
                            item,
                            (list, tuple),
                        )
                        and len(item) >= 2
                    ):

                        lime_rows.append(
                            {
                                "feature":
                                    str(item[0]),
                                "weight":
                                    float(item[1]),
                            }
                        )

                if lime_rows:

                    lime_df = pd.DataFrame(
                        lime_rows
                    )

                    st.subheader(
                        "LIME Local Explanation"
                    )

                    numeric_column = None

                    for column in [
                        "weight",
                        "lime_value",
                        "impact",
                        "score",
                    ]:

                        if column in lime_df.columns:

                            numeric_column = column
                            break

                    if numeric_column:

                        chart_df = lime_df[
                            [
                                "feature",
                                numeric_column,
                            ]
                        ].copy()

                        chart_df[
                            numeric_column
                        ] = pd.to_numeric(
                            chart_df[
                                numeric_column
                            ],
                            errors="coerce",
                        )

                        chart_df = chart_df.dropna()

                        st.bar_chart(
                            chart_df.set_index(
                                "feature"
                            )[numeric_column]
                        )

                    st.dataframe(
                        lime_df,
                        use_container_width=True,
                        hide_index=True,
                    )

            with st.expander(
                "Raw LIME Response"
            ):

                st.json(result)

        else:

            st.error(
                "LIME explanation failed."
            )

            st.json(result)


# ============================================================
# REVENUE SIMULATION
# ============================================================

elif page == "🧮 Revenue Simulation":

    st.title(
        "🧮 Revenue & Profit Simulation"
    )

    st.write(
        "Evaluate the financial impact of a pricing scenario."
    )

    st.divider()

    with st.form("revenue_form"):

        c1, c2, c3 = st.columns(3)

        with c1:

            price = st.number_input(
                "Selling Price",
                min_value=0.01,
                value=1350.0,
                step=10.0,
            )

        with c2:

            quantity = st.number_input(
                "Expected Quantity",
                min_value=0,
                value=10,
                step=1,
            )

        with c3:

            cost = st.number_input(
                "Cost Per Unit",
                min_value=0.0,
                value=950.0,
                step=10.0,
            )

        submitted = st.form_submit_button(
            "🧮 Simulate Revenue",
            use_container_width=True,
        )

    if submitted:

        payload = {
            "price": price,
            "expected_quantity": int(
                quantity
            ),
            "cost_per_unit": cost,
        }

        with st.spinner(
            "Calculating financial impact..."
        ):

            success, result = post_api(
                "/pricing/simulate-revenue",
                payload,
            )

        if success:

            st.success(
                "Revenue simulation completed."
            )

            c1, c2, c3, c4 = st.columns(4)

            with c1:

                st.metric(
                    "Expected Revenue",
                    money(
                        result.get(
                            "expected_revenue"
                        )
                    ),
                )

            with c2:

                st.metric(
                    "Total Cost",
                    money(
                        result.get(
                            "total_cost"
                        )
                    ),
                )

            with c3:

                st.metric(
                    "Expected Profit",
                    money(
                        result.get(
                            "expected_profit"
                        )
                    ),
                )

            with c4:

                st.metric(
                    "Profit Margin",
                    percentage(
                        result.get(
                            "profit_margin_percentage"
                        )
                    ),
                )

            st.divider()

            financial_df = pd.DataFrame(
                {
                    "Metric": [
                        "Selling Price",
                        "Expected Quantity",
                        "Cost Per Unit",
                        "Expected Revenue",
                        "Total Cost",
                        "Expected Profit",
                        "Profit Margin",
                    ],
                    "Value": [
                        money(price),
                        f"{int(quantity):,}",
                        money(cost),
                        money(
                            result.get(
                                "expected_revenue"
                            )
                        ),
                        money(
                            result.get(
                                "total_cost"
                            )
                        ),
                        money(
                            result.get(
                                "expected_profit"
                            )
                        ),
                        percentage(
                            result.get(
                                "profit_margin_percentage"
                            )
                        ),
                    ],
                }
            )

            financial_df["Value"] = financial_df[
                "Value"
            ].astype(str)

            st.dataframe(
                financial_df,
                use_container_width=True,
                hide_index=True,
            )

            chart_df = pd.DataFrame(
                {
                    "Financial Metric": [
                        "Revenue",
                        "Cost",
                        "Profit",
                    ],
                    "Amount": [
                        result.get(
                            "expected_revenue",
                            0,
                        ),
                        result.get(
                            "total_cost",
                            0,
                        ),
                        result.get(
                            "expected_profit",
                            0,
                        ),
                    ],
                }
            )

            st.subheader(
                "Financial Breakdown"
            )

            st.bar_chart(
                chart_df.set_index(
                    "Financial Metric"
                )
            )

            with st.expander(
                "Raw Simulation Response"
            ):

                st.json(result)

        else:

            st.error(
                "Revenue simulation failed."
            )

            st.json(result)


# ============================================================
# SYSTEM HEALTH
# ============================================================

elif page == "❤️ System Health":

    st.title(
        "❤️ Platform Health"
    )

    st.write(
        "Monitor the services supporting the Dynamic Pricing platform."
    )

    if st.button(
        "🔄 Refresh Status",
        width="stretch",
    ):

        st.rerun()

    st.divider()

    api_ok, api_data = get_api(
        "/health"
    )

    redis_ok, redis_data = get_api(
        "/health/redis"
    )

    c1, c2, c3 = st.columns(3)

    with c1:

        if api_ok:
            st.success("FASTAPI ONLINE")
        else:
            st.error("FASTAPI OFFLINE")

    with c2:

        if redis_ok:
            st.success("REDIS ONLINE")
        else:
            st.error("REDIS OFFLINE")

    with c3:

        st.success("STREAMLIT ONLINE")

    st.divider()

    st.subheader(
        "Service Status"
    )

    health_table = pd.DataFrame(
        [
            [
                "FastAPI",
                "127.0.0.1:8000",
                "ONLINE" if api_ok else "OFFLINE",
            ],
            [
                "Redis",
                "localhost:6379",
                "ONLINE" if redis_ok else "OFFLINE",
            ],
            [
                "SQLite",
                "dynamic_pricing.db",
                "ACTIVE",
            ],
            [
                "XGBoost",
                "Forecast Model",
                "READY",
            ],
            [
                "SHAP",
                "Explainability",
                "READY",
            ],
            [
                "LIME",
                "Explainability",
                "READY",
            ],
            [
                "MLflow",
                "Experiment Tracking",
                "INTEGRATED",
            ],
        ],
        columns=[
            "Service",
            "Location",
            "Status",
        ],
    )

    st.dataframe(
        health_table,
        width="stretch",
        hide_index=True,
    )

    st.subheader(
        "FastAPI Health Response"
    )

    if api_ok:
        st.json(api_data)
    else:
        st.error(api_data)

    st.subheader(
        "Redis Health Response"
    )

    if redis_ok:
        st.json(redis_data)
    else:
        st.error(redis_data)


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer">

        Enterprise Dynamic Pricing Intelligence Platform

        <br>

        FastAPI • XGBoost • Dynamic Pricing • Redis
        • MLflow • SHAP • LIME • Streamlit

    </div>
    """,
    unsafe_allow_html=True,
)