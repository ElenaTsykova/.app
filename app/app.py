import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# 🎯 Настройки страницы
st.set_page_config(page_title="Отчёт по простоям", layout="wide")

# 📥 Загрузка данных
st.sidebar.header("Загрузка данных")
uploaded_file = st.sidebar.file_uploader("Выберите Excel-файл", type=["xlsx"])

if uploaded_file:
    # Загрузка данных из Excel
    df = pd.read_excel(uploaded_file, parse_dates=['time'])

    # 🗓️ Создание столбца месяца
    df['mon'] = df['time'].dt.to_period('M').dt.to_timestamp()

    # 📊 Метрики
    min_date = df['time'].min()
    max_date = df['time'].max()

    time_difference = max_date - min_date
    time_days = time_difference.days
    time_weeks = time_days // 7  
    time_months = time_days / 30 

    total_downtime = df['downtime'].sum()
    total_events = df['id'].count()

    st.title("📈 Аналитика простоев оборудования")
    st.subheader(f"Данные с {min_date.date()} по {max_date.date()}")
    col1, col2, col3 = st.columns(3)
    col1.metric("Общее количество простоев", total_events)
    col2.metric("Общая длительность", f"{total_downtime} мин = {total_downtime // 60} ч")
    col3.metric("Средняя длительность", f"{round(df['downtime'].mean())} мин.")

    st.markdown("---")

    # 💡 Доп. метрики
    st.subheader("📊 Метрики MTBF / MTTR")

    col4, col5, col6 = st.columns(3)
    col4.metric("Период", f"{time_days} дней ({round(time_months, 1)} мес.)")
    col5.metric("MTBF", f"{round(time_days * 24 / total_events)} ч.")
    col6.metric("MTTR", f"{round(total_downtime / total_events)} мин.")

    st.markdown("---")

    # 📈 График динамики простоев по отделам по месяцам
    st.subheader("📉 Динамика количества простоев по отделам по месяцам")

    grouped = df.groupby(['mon', 'department']).size().reset_index(name='Количество простоев')
    pivot_df = grouped.pivot(index='mon', columns='department', values='Количество простоев').fillna(0)

    fig1, ax1 = plt.subplots(figsize=(10, 4))
    pivot_df.plot(kind='line', marker='o', ax=ax1, color=['#7B68EE', '#FF6F61', '#20B2AA'])
    ax1.set_title('Простои по отделам по месяцам')
    ax1.set_xlabel('Месяц')
    ax1.set_ylabel('Количество простоев')
    ax1.tick_params(axis='x', rotation=45)
    ax1.grid(True)
    st.pyplot(fig1)

    st.markdown("---")

    # 📊 Два горизонтальных графика: по отделам и по линиям
    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("🔧 Количество простоев по цехам")
        departments = df.groupby('department').agg({'id': 'count'}).sort_values(by='id')
        fig2, ax2 = plt.subplots(figsize=(6.5, 4))
        departments.plot(kind='barh', legend=False, ax=ax2, color='#7B68EE')
        ax2.set_xlabel('Количество простоев')
        ax2.set_ylabel('Цех')
        ax2.set_title('Количество простоев по цехам')
        for i, v in enumerate(departments['id']):
            ax2.text(v + 0.5, i, f'{v:.0f}', va='center')
        st.pyplot(fig2)

    with col_b:
        st.subheader("🏭 ТОП-10 линий по количеству простоев")
        lines = df.groupby('line').agg({'id': 'count'}).sort_values(by='id').tail(10)
        fig3, ax3 = plt.subplots(figsize=(6.5, 4))
        lines.plot(kind='barh', legend=False, ax=ax3, color='#7B68EE')
        ax3.set_xlabel('Количество простоев')
        ax3.set_ylabel('Линия')
        ax3.set_title('ТОП-10 линий по количеству простоев')
        for i, v in enumerate(lines['id']):
            ax3.text(v + 0.5, i, f'{v:.0f}', va='center')
        st.pyplot(fig3)
