function Welcome({ data }) {
  if (!data) return <div>Loading...</div>

  return (
    <div className="welcome-container">
      <h1>{data.title}</h1>
      <p>{data.description}</p>
      <p>Version: {data.version}</p>
    </div>
  )
}

export default Welcome