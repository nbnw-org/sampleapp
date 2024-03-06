import './App.css'
import { post } from 'aws-amplify/api';

function App() {
  const article = {
    id: "news10",
  };

  return (
    <>
      <div>
        <button onClick={() => {
          console.log("Clicked");
          post({
            apiName: 'sampleappapi',
            path: '/approve',
            options: {
              body: {...article}
            }
          }).response.then(response => {
            console.log(response);
          }).catch(error => {
            console.log(error);
          });
          
          }}>Create News</button>
      </div>
      <p className="read-the-docs">
        Click on the Vite and React logos to learn more
      </p>
    </>
  )
}

export default App
