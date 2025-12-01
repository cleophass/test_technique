docker-compose up -d

echo "Attente d'Elasticsearch..."
until curl -s http://localhost:9200/_cluster/health | grep -q '"status":"green"\|"status":"yellow"'; do
  echo "Elasticsearch n'est pas encore prêt..."
  sleep 10
done
echo "Elasticsearch est prêt."

echo "Attente de Kibana..."
until curl -s http://localhost:5601/api/status | grep -q '"level":"available"'; do
  echo "Kibana n'est pas encore prêt..."
  sleep 10
done
echo "Kibana est prêt."

echo "Démarrage de l'application Streamlit..."
uv run python -m streamlit run app/Chatbot.py