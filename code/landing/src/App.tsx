import Tags from "./componants/Tags"
import  Button  from "./componants/Button"
import Problem from "./componants/Problem"

// Assets
import image_network from "./assets/network.png"
import image_discord from "./assets/discord.png"
import image_support from "./assets/support.png"

import image_research_travel from "./assets/research_travel.jpg"
import image_unexpected from "./assets/unexpected.jpg"
import image_lang from "./assets/lang.png"


const problems = [
  {
    title: "Le chaos des recherches infinies",
    text: 
    "Passer des heures à rechercher des informations sur les voyages est devenu la norme."+
    "Entre les dizaines de sites, les avis contradictoires et les informations dispersées, organiser un voyage peut vite devenir frustrant et chronophage.",
    image: image_research_travel,
  },
  {
    title: "Le stress des imprévus 24h/24",
    text: 
    "Les imprévus peuvent gâcher un voyage à tout moment : annulation de vol, perte de bagages ou changement de plan de dernière minute.\n"+
    "Sans assistance immédiate, ces situations deviennent vite stressantes et compliquent votre séjour.",
    image: image_unexpected,
  },
  {
    title: "La barrière des langues",
    text: "Préparer un voyage à l’étranger peut vite devenir compliqué lorsque l’on ne maîtrise pas la langue locale.\n"+
    "Rechercher des activités, lire les avis, comparer les options ou comprendre les sites locaux devient rapidement frustrant et chronophage.",
    image: image_lang,
  },
];

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
      {/* Problematique */}
      <div>
        <h1 className="font-bold text-4xl text-center mt-16 mb-32">
  Organiser un voyage peut être complexe et chronophage. Notre solution vise à simplifier ce processus.
        </h1>

        <div>
          {problems.map((problem, index) => (
            <Problem
              key={index}
              title={problem.title}
              text={problem.text}
              image={problem.image}
              reverse={index % 2 === 0}
            />
          ))}
        </div>
    </div>
      

    </div>

  )
}

export default App
