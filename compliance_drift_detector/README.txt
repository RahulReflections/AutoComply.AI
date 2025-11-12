1. Place your SSH-accessible Linux VM IP, username, and password in collector.py.
2. Run collector.py to fetch configuration data.
3. Run detect.py to compare results with policies and flag drift.
4. Start the dashboard: streamlit run src/app.py
5. Review detected drifts and recommended remediations in browser.
