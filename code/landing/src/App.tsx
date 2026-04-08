import Tags from "./componants/Tags"
import  Button  from "./componants/Button"

// Assets
import image_network from "./assets/network.png"
import image_discord from "./assets/discord.png"
import image_support from "./assets/support.png"

function App() {
  return (
    <div>

      {/* Header */}
      <div className="flex flex-col items-center w-full pt-48 h-[80vh] bg-[linear-gradient(135deg,#ffffff_0%,#AFA4DB_60%,#66EDD9_100%)] gap-4">
        <h1 className="text-4xl font-bold text-black text-center ">
          ChatTPG <br/>
          Organisez vos voyages efficacement
          </h1>

        <p className="text-lg text-gray-700 text-center">
          Discuter avec notre chatbot disponible 24h/24, 7j/7.  
        </p>

          <div className="flex items-center justify-center gap-8 mt-16">
            <Tags image={image_network} title="Disponible 24h/24, 7j/7" />
          <Tags image={image_discord} title="Utilisable via Discord" />
          <Tags image={image_support} title="Assistance personnalisée" />
          </div>
          <div className="flex items-center justify-center gap-8 mt-16">
          <Button title="Essayer gratuitement" transparent={false} onClick={() => {}} />
          <Button title="Essayer une Démo" transparent={true} onClick={() => {}} />
          </div>
      </div>

    </div>

  )
}

export default App
