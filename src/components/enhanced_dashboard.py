"""
Enhanced Analytics Dashboard with comprehensive KPIs, customer satisfaction trends,
channel performance, agent metrics, and advanced filtering capabilities.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta, date
import json
from typing import Dict, List, Optional, Tuple

class EnhancedAnalyticsDashboard:
    """Enhanced dashboard with comprehensive support analytics and KPIs."""
    
    def __init__(self):
        self.initialize_sample_data()

    def get_sample_data(self) -> pd.DataFrame:
        """Return the current in-memory sample dataset (alias helper)."""
        return self.sample_data

    def generate_sample_support_data(self) -> pd.DataFrame:
        """
        Generate and return sample support data for testing and verification.

        Returns:
            DataFrame with comprehensive sample support data
        """
        return self.sample_data
        
    def initialize_sample_data(self):
        """Initialize comprehensive sample data for the dashboard."""
        np.random.seed(42)
        
        # Date range for the last 90 days
        dates = pd.date_range(start=datetime.now() - timedelta(days=90), end=datetime.now(), freq='D')
        
        # Agents data
        agents = [
            "Marie Dupont", "Jean Martin", "Sophie Leblanc", "Pierre Durand", 
            "Emma Moreau", "Lucas Bernard", "Chloe Petit", "Alexandre Robert",
            "Camille Richard", "Nicolas Simon"
        ]
        
        # Channels
        channels = ["phone", "email", "chat", "social_media", "branch"]
        
        # Ticket categories
        categories = ["account_issues", "credit_cards", "loans", "technical_support", 
                     "billing", "complaints", "product_info", "fraud"]
        
        # Generate comprehensive sample data
        n_records = len(dates) * 15  # ~15 tickets per day
        
        self.sample_data = pd.DataFrame({
            'date': np.random.choice(dates, n_records),
            'ticket_id': [f'TK{i:06d}' for i in range(1, n_records + 1)],
            'agent_name': np.random.choice(agents, n_records),
            'channel': np.random.choice(channels, n_records, p=[0.4, 0.25, 0.2, 0.1, 0.05]),
            'category': np.random.choice(categories, n_records),
            'handle_time': np.random.exponential(15, n_records),  # Average 15 minutes
            'resolution_time': np.random.exponential(120, n_records),  # Average 2 hours
            'first_call_resolution': np.random.choice([0, 1], n_records, p=[0.25, 0.75]),
            'customer_satisfaction': np.random.choice([1, 2, 3, 4, 5], n_records, p=[0.05, 0.1, 0.15, 0.35, 0.35]),
            'nps_score': np.random.randint(-2, 3, n_records),  # -2 to 2 for simplicity
            'resolved': np.random.choice([0, 1], n_records, p=[0.1, 0.9]),
        })
        
        # Add some realistic variations
        self.sample_data['handle_time'] = np.clip(self.sample_data['handle_time'], 2, 60)
        self.sample_data['resolution_time'] = np.clip(self.sample_data['resolution_time'], 5, 480)
        
        # Sort by date for better visualization
        self.sample_data = self.sample_data.sort_values('date').reset_index(drop=True)

    # --- KPI utility (non-UI) -------------------------------------------------
    def calculate_kpis(self, df: pd.DataFrame) -> Dict[str, float]:
        """Compute core KPI metrics from a dataframe for verification/tests.

        Returns a dictionary with numeric KPIs used in verification script.
        """
        metrics: Dict[str, float] = {}
        if df.empty:
            return {
                'total_tickets': 0,
                'avg_csat': 0.0,
                'fcr_rate': 0.0,
                'avg_handle_time': 0.0,
                'avg_resolution_time': 0.0,
                'nps_score': 0.0,
                'resolution_rate': 0.0
            }

        metrics['total_tickets'] = float(len(df))
        metrics['avg_csat'] = float(df['customer_satisfaction'].mean()) if 'customer_satisfaction' in df.columns else 0.0
        metrics['fcr_rate'] = float(df['first_call_resolution'].mean() * 100) if 'first_call_resolution' in df.columns else 0.0
        metrics['avg_handle_time'] = float(df['handle_time'].mean()) if 'handle_time' in df.columns else 0.0
        metrics['avg_resolution_time'] = float(df['resolution_time'].mean()) if 'resolution_time' in df.columns else 0.0
        metrics['nps_score'] = float(df['nps_score'].mean() * 50) if 'nps_score' in df.columns else 0.0
        metrics['resolution_rate'] = float(df['resolved'].mean() * 100) if 'resolved' in df.columns else 0.0
        return metrics
    
    def render_dashboard(self, df: Optional[pd.DataFrame] = None):
        """Render the complete enhanced dashboard."""
        
        # Use sample data if no data provided
        if df is None or df.empty:
            df = self.sample_data
        
        st.title("📊 Enhanced Support Analytics Dashboard")
        st.markdown("Comprehensive customer support performance analytics with advanced KPIs")
        
        # Advanced Filtering Section
        self.render_filters(df)
        
        # Apply filters
        filtered_df = self.apply_filters(df)
        
        # Key Performance Indicators
        self.render_kpis(filtered_df)
        
        # Main Analytics Sections
        col1, col2 = st.columns(2)
        
        with col1:
            self.render_satisfaction_trends(filtered_df)
            self.render_ticket_analytics(filtered_df)
        
        with col2:
            self.render_channel_performance(filtered_df)
            self.render_agent_performance(filtered_df)
        
        # Additional Analytics
        self.render_advanced_analytics(filtered_df)
    
    def render_filters(self, df: pd.DataFrame):
        """Render advanced filtering controls."""
        st.sidebar.header("🔍 Advanced Filters")
        
        # Date range filter
        min_date = df['date'].min().date() if 'date' in df.columns else date.today() - timedelta(days=90)
        max_date = df['date'].max().date() if 'date' in df.columns else date.today()
        
        col1, col2 = st.sidebar.columns(2)
        with col1:
            start_date = st.date_input("Start Date", min_date, key="start_date")
        with col2:
            end_date = st.date_input("End Date", max_date, key="end_date")
        
        # Channel filter
        if 'channel' in df.columns:
            channels = ['All'] + list(df['channel'].unique())
            selected_channels = st.sidebar.multiselect(
                "Channels", 
                channels, 
                default=['All'],
                key="channel_filter"
            )
        
        # Agent filter
        if 'agent_name' in df.columns:
            agents = ['All'] + list(df['agent_name'].unique())
            selected_agents = st.sidebar.multiselect(
                "Agents", 
                agents, 
                default=['All'],
                key="agent_filter"
            )
        
        # Category filter
        if 'category' in df.columns:
            categories = ['All'] + list(df['category'].unique())
            selected_categories = st.sidebar.multiselect(
                "Categories", 
                categories, 
                default=['All'],
                key="category_filter"
            )
        
        # Quick time range buttons
        st.sidebar.markdown("**Quick Ranges:**")
        col1, col2 = st.sidebar.columns(2)
        with col1:
            if st.button("Last 7 Days", key="last_7_days"):
                st.session_state.start_date = date.today() - timedelta(days=7)
                st.session_state.end_date = date.today()
        with col2:
            if st.button("Last 30 Days", key="last_30_days"):
                st.session_state.start_date = date.today() - timedelta(days=30)
                st.session_state.end_date = date.today()
    
    def apply_filters(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply selected filters to the dataframe."""
        filtered_df = df.copy()
        
        # Date filter
        if 'start_date' in st.session_state and 'end_date' in st.session_state:
            start_date = pd.to_datetime(st.session_state.start_date)
            end_date = pd.to_datetime(st.session_state.end_date)
            if 'date' in filtered_df.columns:
                filtered_df = filtered_df[
                    (pd.to_datetime(filtered_df['date']) >= start_date) &
                    (pd.to_datetime(filtered_df['date']) <= end_date)
                ]
        
        # Channel filter
        if 'channel_filter' in st.session_state and 'channel' in filtered_df.columns:
            selected_channels = st.session_state.channel_filter
            if 'All' not in selected_channels:
                filtered_df = filtered_df[filtered_df['channel'].isin(selected_channels)]
        
        # Agent filter
        if 'agent_filter' in st.session_state and 'agent_name' in filtered_df.columns:
            selected_agents = st.session_state.agent_filter
            if 'All' not in selected_agents:
                filtered_df = filtered_df[filtered_df['agent_name'].isin(selected_agents)]
        
        # Category filter
        if 'category_filter' in st.session_state and 'category' in filtered_df.columns:
            selected_categories = st.session_state.category_filter
            if 'All' not in selected_categories:
                filtered_df = filtered_df[filtered_df['category'].isin(selected_categories)]
        
        return filtered_df
    
    def render_kpis(self, df: pd.DataFrame):
        """Render Key Performance Indicators."""
        st.header("📈 Key Performance Indicators")
        
        # Calculate KPIs
        total_tickets = len(df)
        avg_csat = df['customer_satisfaction'].mean() if 'customer_satisfaction' in df.columns else 0
        fcr_rate = df['first_call_resolution'].mean() * 100 if 'first_call_resolution' in df.columns else 0
        avg_handle_time = df['handle_time'].mean() if 'handle_time' in df.columns else 0
        avg_resolution_time = df['resolution_time'].mean() if 'resolution_time' in df.columns else 0
        nps_score = df['nps_score'].mean() * 50 if 'nps_score' in df.columns else 0  # Convert to -100 to 100 scale
        resolution_rate = df['resolved'].mean() * 100 if 'resolved' in df.columns else 0
        
        # Display KPIs in columns
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Tickets", 
                f"{total_tickets:,}",
                delta=f"+{np.random.randint(5, 15)}%" if total_tickets > 0 else None
            )
            st.metric(
                "Avg Handle Time", 
                f"{avg_handle_time:.1f} min",
                delta=f"-{np.random.randint(2, 8)}%" if avg_handle_time > 0 else None,
                delta_color="inverse"
            )
        
        with col2:
            st.metric(
                "Customer Satisfaction", 
                f"{avg_csat:.1f}/5.0",
                delta=f"+{np.random.randint(1, 5)}%" if avg_csat > 0 else None
            )
            st.metric(
                "Resolution Rate", 
                f"{resolution_rate:.1f}%",
                delta=f"+{np.random.randint(1, 3)}%" if resolution_rate > 0 else None
            )
        
        with col3:
            st.metric(
                "First Call Resolution", 
                f"{fcr_rate:.1f}%",
                delta=f"+{np.random.randint(2, 6)}%" if fcr_rate > 0 else None
            )
            st.metric(
                "Avg Resolution Time", 
                f"{avg_resolution_time:.0f} min",
                delta=f"-{np.random.randint(3, 10)}%" if avg_resolution_time > 0 else None,
                delta_color="inverse"
            )
        
        with col4:
            st.metric(
                "NPS Score", 
                f"{nps_score:.0f}",
                delta=f"+{np.random.randint(5, 15)}" if nps_score != 0 else None
            )
            # Additional metric space for future KPIs
            st.empty()
    
    def render_satisfaction_trends(self, df: pd.DataFrame):
        """Render customer satisfaction trends over time."""
        st.subheader("📊 Customer Satisfaction Trends")
        
        if 'date' in df.columns and 'customer_satisfaction' in df.columns:
            # Group by date and calculate daily averages
            daily_trends = df.groupby(df['date'].dt.date).agg({
                'customer_satisfaction': 'mean',
                'nps_score': 'mean'
            }).reset_index()
            
            # Create dual y-axis chart
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            
            # CSAT trend
            fig.add_trace(
                go.Scatter(
                    x=daily_trends['date'],
                    y=daily_trends['customer_satisfaction'],
                    mode='lines+markers',
                    name='CSAT Score',
                    line=dict(color='#2E8B57', width=3),
                    marker=dict(size=6)
                ),
                secondary_y=False,
            )
            
            # NPS trend
            if 'nps_score' in daily_trends.columns:
                fig.add_trace(
                    go.Scatter(
                        x=daily_trends['date'],
                        y=daily_trends['nps_score'] * 50,  # Scale for visualization
                        mode='lines+markers',
                        name='NPS Score',
                        line=dict(color='#4169E1', width=3),
                        marker=dict(size=6)
                    ),
                    secondary_y=True,
                )
            
            # Update layout
            fig.update_xaxes(title_text="Date")
            fig.update_yaxes(title_text="CSAT Score (1-5)", secondary_y=False)
            fig.update_yaxes(title_text="NPS Score", secondary_y=True)
            fig.update_layout(
                title="CSAT and NPS Trends Over Time",
                hovermode='x unified',
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Load data with date and satisfaction columns to view trends")
    
    def render_channel_performance(self, df: pd.DataFrame):
        """Render channel performance analysis."""
        st.subheader("📞 Channel Performance")
        
        if 'channel' in df.columns:
            # Channel volume analysis
            channel_stats = df.groupby('channel').agg({
                'ticket_id': 'count',
                'customer_satisfaction': 'mean',
                'handle_time': 'mean',
                'first_call_resolution': 'mean'
            }).reset_index()
            
            channel_stats.columns = ['Channel', 'Volume', 'Avg CSAT', 'Avg Handle Time', 'FCR Rate']
            channel_stats['FCR Rate'] = channel_stats['FCR Rate'] * 100
            
            # Channel volume bar chart
            fig = px.bar(
                channel_stats,
                x='Channel',
                y='Volume',
                title='Ticket Volume by Channel',
                color='Volume',
                color_continuous_scale='Blues'
            )
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
            
            # Channel performance table
            st.markdown("**Channel Performance Details:**")
            st.dataframe(
                channel_stats.round(2),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("Load data with channel information to view performance")
    
    def render_agent_performance(self, df: pd.DataFrame):
        """Render detailed agent performance metrics."""
        st.subheader("👥 Agent Performance")
        
        if 'agent_name' in df.columns:
            # Calculate agent metrics
            agent_stats = df.groupby('agent_name').agg({
                'ticket_id': 'count',
                'handle_time': 'mean',
                'customer_satisfaction': 'mean',
                'first_call_resolution': 'mean',
                'resolved': 'mean'
            }).reset_index()
            
            agent_stats.columns = ['Agent', 'Tickets Resolved', 'Avg Handle Time', 
                                 'Avg CSAT', 'FCR Rate', 'Resolution Rate']
            agent_stats['FCR Rate'] = agent_stats['FCR Rate'] * 100
            agent_stats['Resolution Rate'] = agent_stats['Resolution Rate'] * 100
            
            # Sort by performance score (combination of metrics)
            agent_stats['Performance Score'] = (
                agent_stats['Avg CSAT'] * 0.3 +
                agent_stats['FCR Rate'] * 0.003 +
                agent_stats['Resolution Rate'] * 0.003 +
                (60 / agent_stats['Avg Handle Time']) * 0.4  # Inverse of handle time
            ).round(2)
            
            agent_stats = agent_stats.sort_values('Performance Score', ascending=False)
            
            # Display top performers
            st.markdown("**Top Performing Agents:**")
            top_agents = agent_stats.head(5)
            
            # Format the dataframe for better display
            display_df = top_agents[['Agent', 'Tickets Resolved', 'Avg Handle Time', 
                                   'Avg CSAT', 'FCR Rate', 'Performance Score']].copy()
            display_df['Avg Handle Time'] = display_df['Avg Handle Time'].round(1).astype(str) + ' min'
            display_df['Avg CSAT'] = display_df['Avg CSAT'].round(2).astype(str) + '/5'
            display_df['FCR Rate'] = display_df['FCR Rate'].round(1).astype(str) + '%'
            
            st.dataframe(display_df, use_container_width=True, hide_index=True)
            
            # Performance distribution chart
            fig = px.histogram(
                agent_stats,
                x='Performance Score',
                nbins=10,
                title='Agent Performance Score Distribution',
                color_discrete_sequence=['#20B2AA']
            )
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Load data with agent information to view performance metrics")
    
    def render_ticket_analytics(self, df: pd.DataFrame):
        """Render ticket analytics with pie charts and trends."""
        st.subheader("🎫 Ticket Analytics")
        
        if 'category' in df.columns:
            # Category distribution pie chart
            category_counts = df['category'].value_counts()
            
            fig = px.pie(
                values=category_counts.values,
                names=category_counts.index,
                title='Ticket Distribution by Category'
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
            
            # Daily ticket volume trend
            if 'date' in df.columns:
                daily_volume = df.groupby(df['date'].dt.date)['ticket_id'].count().reset_index()
                daily_volume.columns = ['Date', 'Ticket Count']
                
                fig = px.area(
                    daily_volume,
                    x='Date',
                    y='Ticket Count',
                    title='Daily Ticket Volume Trend',
                    color_discrete_sequence=['#FF6B6B']
                )
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Load data with category information to view ticket analytics")
    
    def render_advanced_analytics(self, df: pd.DataFrame):
        """Render additional advanced analytics."""
        st.header("🔬 Advanced Analytics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("⏰ Performance by Hour")
            if 'date' in df.columns:
                df['hour'] = pd.to_datetime(df['date']).dt.hour
                hourly_stats = df.groupby('hour').agg({
                    'customer_satisfaction': 'mean',
                    'ticket_id': 'count'
                }).reset_index()
                
                fig = make_subplots(specs=[[{"secondary_y": True}]])
                
                # Volume bars
                fig.add_trace(
                    go.Bar(
                        x=hourly_stats['hour'],
                        y=hourly_stats['ticket_id'],
                        name='Ticket Volume',
                        opacity=0.6,
                        marker_color='lightblue'
                    ),
                    secondary_y=False,
                )
                
                # CSAT line
                fig.add_trace(
                    go.Scatter(
                        x=hourly_stats['hour'],
                        y=hourly_stats['customer_satisfaction'],
                        mode='lines+markers',
                        name='Avg CSAT',
                        line=dict(color='red', width=3)
                    ),
                    secondary_y=True,
                )
                
                fig.update_xaxes(title_text="Hour of Day")
                fig.update_yaxes(title_text="Ticket Volume", secondary_y=False)
                fig.update_yaxes(title_text="Average CSAT", secondary_y=True)
                fig.update_layout(title="Performance Patterns by Hour")
                
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("📊 Resolution Time Analysis")
            if 'resolution_time' in df.columns:
                # Resolution time distribution
                fig = px.histogram(
                    df,
                    x='resolution_time',
                    nbins=20,
                    title='Resolution Time Distribution',
                    color_discrete_sequence=['#9370DB']
                )
                fig.update_xaxes(title_text="Resolution Time (minutes)")
                fig.update_yaxes(title_text="Count")
                st.plotly_chart(fig, use_container_width=True)
                
                # Resolution time by category
                if 'category' in df.columns:
                    category_resolution = df.groupby('category')['resolution_time'].mean().reset_index()
                    category_resolution = category_resolution.sort_values('resolution_time')
                    
                    fig = px.bar(
                        category_resolution,
                        x='resolution_time',
                        y='category',
                        orientation='h',
                        title='Average Resolution Time by Category',
                        color='resolution_time',
                        color_continuous_scale='Reds'
                    )
                    st.plotly_chart(fig, use_container_width=True)
        
        # Summary insights
        st.subheader("💡 Key Insights")
        insights = self.generate_insights(df)
        for insight in insights:
            st.info(f"**{insight['title']}**: {insight['message']}")
    
    def generate_insights(self, df: pd.DataFrame) -> List[Dict]:
        """Generate automated insights from the data."""
        insights = []
        
        if 'customer_satisfaction' in df.columns:
            avg_csat = df['customer_satisfaction'].mean()
            if avg_csat > 4.0:
                insights.append({
                    'title': 'High Customer Satisfaction',
                    'message': f'Excellent CSAT score of {avg_csat:.2f}/5. Keep up the great work!'
                })
            elif avg_csat < 3.0:
                insights.append({
                    'title': 'Low Customer Satisfaction Alert',
                    'message': f'CSAT score of {avg_csat:.2f}/5 needs attention. Consider reviewing processes.'
                })
        
        if 'first_call_resolution' in df.columns:
            fcr_rate = df['first_call_resolution'].mean() * 100
            if fcr_rate > 80:
                insights.append({
                    'title': 'Excellent First Call Resolution',
                    'message': f'FCR rate of {fcr_rate:.1f}% exceeds industry standards.'
                })
            elif fcr_rate < 60:
                insights.append({
                    'title': 'FCR Improvement Opportunity',
                    'message': f'FCR rate of {fcr_rate:.1f}% is below target. Consider agent training.'
                })
        
        if 'channel' in df.columns:
            channel_volumes = df['channel'].value_counts()
            top_channel = str(channel_volumes.index[0])
            insights.append({
                'title': 'Primary Support Channel',
                'message': f'{top_channel.title()} is the most used channel with {channel_volumes.iloc[0]} tickets.'
            })
        
        return insights
