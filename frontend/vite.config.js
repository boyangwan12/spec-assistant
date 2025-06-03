export default {
  server: {
    proxy: {
      '/upload': 'http://127.0.0.1:8000',
      '/parse': 'http://127.0.0.1:8000',
      '/chunk': 'http://127.0.0.1:8000',
      '/embed': 'http://127.0.0.1:8000',
      '/chat': 'http://127.0.0.1:8000',
      '/pdf': 'http://127.0.0.1:8000'
    }
  }
}
