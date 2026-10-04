import streamlit as st
import boto3
import time


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="AWS Event Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    /* ========================================================
       KPI CARDS
       ======================================================== */

    .metric-card {
        background: #1e293b;
        padding: 22px;
        border-radius: 12px;
        text-align: center;
        border: 1px solid #334155;
        margin-bottom: 10px;
    }

    .metric-title {
        color: #94a3b8;
        font-size: 14px;
        margin-bottom: 8px;
    }

    .metric-value {
        color: white;
        font-size: 32px;
        font-weight: bold;
    }


    /* ========================================================
       VERTICAL BAR CHART
       ======================================================== */

    .vertical-chart-container {
        background: #111827;
        padding: 25px;
        border-radius: 12px;
        border: 1px solid #263244;
        margin-top: 20px;
        margin-bottom: 25px;
    }

    .vertical-chart-title {
        color: white;
        font-size: 20px;
        font-weight: bold;
        margin-bottom: 20px;
    }

    .vertical-chart {
        height: 340px;
        display: flex;
        align-items: flex-end;
        justify-content: center;
        gap: 45px;
        padding: 20px 30px 0 30px;
        border-bottom: 1px solid #475569;
        overflow-x: auto;
    }

    .vertical-bar-column {
        height: 100%;
        min-width: 90px;
        display: flex;
        flex-direction: column;
        justify-content: flex-end;
        align-items: center;
    }

    .vertical-bar-value {
        color: #f8fafc;
        font-size: 14px;
        font-weight: bold;
        margin-bottom: 8px;
    }

    .vertical-bar-area {
        width: 65px;
        height: 230px;
        display: flex;
        align-items: flex-end;
        justify-content: center;
    }

    .vertical-bar-fill {
        width: 65px;
        min-height: 8px;
        background: linear-gradient(
            180deg,
            #38bdf8,
            #2563eb
        );
        border-radius: 8px 8px 0 0;
    }

    .vertical-bar-label {
        color: #cbd5e1;
        font-size: 13px;
        font-weight: 600;
        margin-top: 12px;
        text-align: center;
        white-space: nowrap;
    }


    /* ========================================================
       RECENT EVENTS
       ======================================================== */

    .section-title {
        color: white;
        font-size: 22px;
        font-weight: bold;
        margin-top: 30px;
        margin-bottom: 15px;
    }

    .event-row {
        background: #111827;
        border: 1px solid #263244;
        padding: 14px 16px;
        border-radius: 8px;
        margin-bottom: 9px;
        color: #e5e7eb;
        font-size: 14px;
    }

    .event-id {
        color: #38bdf8;
        font-weight: bold;
    }

    .event-type {
        color: #f8fafc;
        font-weight: bold;
    }

    .event-user {
        color: #cbd5e1;
    }

    .event-page {
        color: #93c5fd;
    }

    .event-time {
        color: #94a3b8;
    }


    /* ========================================================
       DASHBOARD SUBTITLE
       ======================================================== */

    .dashboard-subtitle {
        color: #94a3b8;
        font-size: 14px;
        margin-bottom: 20px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# DASHBOARD TITLE
# ============================================================

st.title("📊 AWS Event Analytics Dashboard")

st.markdown(
    '<div class="dashboard-subtitle">'
    'Amazon Redshift • Amazon Data Firehose • Amazon S3 Event Analytics'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# AWS REDSHIFT CONNECTION
# ============================================================

client = boto3.client(
    "redshift-data",
    region_name="ap-south-1"
)

WORKGROUP = "default-workgroup"
DATABASE = "dev"


# ============================================================
# RUN REDSHIFT QUERY
# ============================================================

def run_query(sql):

    response = client.execute_statement(
        WorkgroupName=WORKGROUP,
        Database=DATABASE,
        Sql=sql
    )

    statement_id = response["Id"]

    while True:

        status = client.describe_statement(
            Id=statement_id
        )

        if status["Status"] == "FINISHED":
            break

        if status["Status"] in [
            "FAILED",
            "ABORTED"
        ]:

            raise Exception(
                status.get(
                    "Error",
                    "Redshift query failed"
                )
            )

        time.sleep(0.5)


    result = client.get_statement_result(
        Id=statement_id
    )


    columns = [
        column["name"]
        for column in result["ColumnMetadata"]
    ]


    rows = []


    for record in result["Records"]:

        row = []


        for value in record:

            if "longValue" in value:

                row.append(
                    value["longValue"]
                )

            elif "doubleValue" in value:

                row.append(
                    value["doubleValue"]
                )

            elif "stringValue" in value:

                row.append(
                    value["stringValue"]
                )

            elif "booleanValue" in value:

                row.append(
                    value["booleanValue"]
                )

            elif "isNull" in value:

                row.append(None)

            else:

                row.append(None)


        rows.append(row)


    return columns, rows


# ============================================================
# VERTICAL BAR CHART FUNCTION
# ============================================================

def create_bar_chart(
    title,
    data,
    value_name
):

    if not data:

        st.info(
            "No data available."
        )

        return


    max_value = max(
        value
        for _, value in data
    )


    html = (
        '<div class="vertical-chart-container">'
        f'<div class="vertical-chart-title">'
        f'{title}'
        '</div>'
        '<div class="vertical-chart">'
    )


    for label, value in data:

        if max_value > 0:

            percentage = (
                value / max_value
            ) * 100

        else:

            percentage = 0


        html += (
            '<div class="vertical-bar-column">'

            '<div class="vertical-bar-value">'
            f'{value} {value_name}'
            '</div>'

            '<div class="vertical-bar-area">'

            f'<div class="vertical-bar-fill" '
            f'style="height:{percentage}%;">'
            '</div>'

            '</div>'

            '<div class="vertical-bar-label">'
            f'{label}'
            '</div>'

            '</div>'
        )


    html += (
        '</div>'
        '</div>'
    )


    st.markdown(
        html,
        unsafe_allow_html=True
    )


# ============================================================
# LOAD DASHBOARD BUTTON
# ============================================================

if st.button("🔄 Load Dashboard"):

    try:

        # ====================================================
        # SUMMARY METRICS
        # ====================================================

        _, rows = run_query(
            """
            SELECT COUNT(*)
            FROM analytics.events;
            """
        )

        total_events = rows[0][0]


        _, rows = run_query(
            """
            SELECT COUNT(DISTINCT user_id)
            FROM analytics.events;
            """
        )

        unique_users = rows[0][0]


        _, rows = run_query(
            """
            SELECT COUNT(DISTINCT event_type)
            FROM analytics.events;
            """
        )

        event_types = rows[0][0]


        _, rows = run_query(
            """
            SELECT COUNT(DISTINCT page)
            FROM analytics.events;
            """
        )

        pages = rows[0][0]


        # ====================================================
        # KPI CARDS
        # ====================================================

        col1, col2, col3, col4 = st.columns(4)


        col1.markdown(
            '<div class="metric-card">'
            '<div class="metric-title">'
            'Total Events'
            '</div>'
            f'<div class="metric-value">'
            f'{total_events}'
            '</div>'
            '</div>',
            unsafe_allow_html=True
        )


        col2.markdown(
            '<div class="metric-card">'
            '<div class="metric-title">'
            'Unique Users'
            '</div>'
            f'<div class="metric-value">'
            f'{unique_users}'
            '</div>'
            '</div>',
            unsafe_allow_html=True
        )


        col3.markdown(
            '<div class="metric-card">'
            '<div class="metric-title">'
            'Event Types'
            '</div>'
            f'<div class="metric-value">'
            f'{event_types}'
            '</div>'
            '</div>',
            unsafe_allow_html=True
        )


        col4.markdown(
            '<div class="metric-card">'
            '<div class="metric-title">'
            'Pages'
            '</div>'
            f'<div class="metric-value">'
            f'{pages}'
            '</div>'
            '</div>',
            unsafe_allow_html=True
        )


        st.divider()


        # ====================================================
        # EVENT TYPE DISTRIBUTION
        # ====================================================

        _, rows = run_query(
            """
            SELECT
                event_type,
                COUNT(*) AS total_events
            FROM analytics.events
            GROUP BY event_type
            ORDER BY total_events DESC;
            """
        )


        event_data = [
            (
                row[0],
                row[1]
            )
            for row in rows
        ]


        create_bar_chart(
            "📈 Event Type Distribution",
            event_data,
            "events"
        )


        # ====================================================
        # PAGE VISIT DISTRIBUTION
        # ====================================================

        _, rows = run_query(
            """
            SELECT
                page,
                COUNT(*) AS total_visits
            FROM analytics.events
            GROUP BY page
            ORDER BY total_visits DESC;
            """
        )


        page_data = [
            (
                row[0],
                row[1]
            )
            for row in rows
        ]


        create_bar_chart(
            "🌐 Page Visit Distribution",
            page_data,
            "visits"
        )


        # ====================================================
        # EVENTS BY USER
        # ====================================================

        _, rows = run_query(
            """
            SELECT
                user_id,
                COUNT(*) AS total_events
            FROM analytics.events
            GROUP BY user_id
            ORDER BY total_events DESC;
            """
        )


        user_data = [
            (
                f"User {row[0]}",
                row[1]
            )
            for row in rows
        ]


        create_bar_chart(
            "👤 Events by User",
            user_data,
            "events"
        )


        # ====================================================
        # EVENTS OVER TIME
        # ====================================================

        _, rows = run_query(
            """
            SELECT
                DATE_TRUNC(
                    'day',
                    event_time
                ) AS event_date,
                COUNT(*) AS total_events
            FROM analytics.events
            GROUP BY event_date
            ORDER BY event_date;
            """
        )


        time_data = [
            (
                str(row[0]).split(" ")[0],
                row[1]
            )
            for row in rows
        ]


        create_bar_chart(
            "📅 Events Over Time",
            time_data,
            "events"
        )


        # ====================================================
        # RECENT EVENTS
        # ====================================================

        st.markdown(
            '<div class="section-title">'
            '📋 Recent Events'
            '</div>',
            unsafe_allow_html=True
        )


        _, rows = run_query(
            """
            SELECT
                event_id,
                event_type,
                user_id,
                page,
                event_time
            FROM analytics.events
            ORDER BY event_time DESC
            LIMIT 20;
            """
        )


        for row in rows:

            event_id = row[0]
            event_type = row[1]
            user_id = row[2]
            page = row[3]
            event_time = row[4]


            event_html = (
                '<div class="event-row">'

                '<span class="event-id">'
                f'Event {event_id}'
                '</span>'

                ' &nbsp; | &nbsp; '

                '<span class="event-type">'
                f'{event_type}'
                '</span>'

                ' &nbsp; | &nbsp; '

                '<span class="event-user">'
                f'User {user_id}'
                '</span>'

                ' &nbsp; | &nbsp; '

                '<span class="event-page">'
                f'{page}'
                '</span>'

                ' &nbsp; | &nbsp; '

                '<span class="event-time">'
                f'{event_time}'
                '</span>'

                '</div>'
            )


            st.markdown(
                event_html,
                unsafe_allow_html=True
            )


        # ====================================================
        # SUCCESS MESSAGE
        # ====================================================

        st.success(
            "Dashboard loaded successfully ✅"
        )


    # ========================================================
    # ERROR HANDLING
    # ========================================================

    except Exception as e:

        st.error(
            "Could not load data from Redshift."
        )

        st.code(
            str(e)
        )