export function Problem({title, text, image, reverse}: {
  title: string;
  text: string;
  image: string;
  reverse: boolean;
}) {
  return reverse ? (
    <div className="flex mt-8 gap-4">
      {/* Partie gauche */}
      <div className="w-[60%] h-[40vh] flex flex-col gap-4 bg-blue-100 rounded-lg ml-4">
        <h1 className="font-bold text-4xl mt-4 ml-4">{title}</h1>
        <p className="p-8 text-gray-700 whitespace-pre-line text-2xl leading-loose">{text}</p>
      </div>

      {/* Partie droite */}
       <div className="w-[40%] h-[40vh] rounded-lg overflow-hidden mr-4">
            <img
                src={image}
                alt="Illustration"
                className="w-full h-full object-cover rounded-lg"
            />
        </div>
    </div>
  ) : (
    <div className="flex mt-8 gap-4">
      {/* Partie gauche */}
      <div className="w-[40%] h-[40vh] rounded-lg ml-4 overflow-hidden">
    <img
      src={image}
      alt="Illustration"
      className="w-full h-full object-cover rounded-lg"
    />
      </div>

      {/* Partie droite */}
      <div className="w-[60%] h-[40vh] flex flex-col gap-4 bg-blue-100 rounded-lg mr-4">
        <h1 className="font-bold text-4xl mt-4 ml-4">{title}</h1>
        <p className="p-8 text-gray-700 text-2xl whitespace-pre-line leading-loose ">{text}</p>
      </div>
    </div>
  );
}

export default Problem;