export function Use({number, title, text}: {
  number: number;
  title: string;
  text: string;
}) {
  return (
    <div className=" flex flex-col w-[30%] h-[30vh] border border-black rounded-md ">
      <div className="flex flex-row ">
        <div className="flex items-center justify-center w-12 h-12 border-2 border-black mt-4 ml-4 rounded-md text-xl font-bold text-white bg-blue-500">
        {number}
        </div>
        <h2 className="text-xl font-semibold mt-6 ml-16">{title}</h2>
      </div>
      
      <p className="text-gray-600 p-4 text-l leading-loose mt-4">{text}</p>
      
    </div>
  )
}

export default Use