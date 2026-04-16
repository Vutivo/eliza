import Button from "./Button";

export function Price({
  title,
  price,
  args,
}: {
  title: string;
  price: string;
  args: { text: string; highlight?: boolean }[];
}) {
  return (
    <div className="h-[50vh] w-[20%] border border-black rounded-md flex flex-col">
      
      <h2 className="text-xl font-bold text-center mt-4">{title}</h2>

      <p className="text-gray-600 text-center mt-4 text-l leading-loose">
        {price}
      </p>

      <div className="flex items-center justify-center mt-4">
        <Button
          title="Choisir cette option"
          transparent={false}
          onClick={() => {}}
        />
      </div>

      <ul className="list-disc list-inside mt-4 p-4">
        {args.map((arg, index) => (
          <li
            key={index}
            className={`text-l leading-loose ${
              arg.highlight ? "text-black font-semibold" : "text-black"
            }`}
          >
            {arg.text}
          </li>
        ))}
      </ul>

    </div>
  );
}

export default Price;