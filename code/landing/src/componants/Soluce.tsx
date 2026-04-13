export function Soluce({title,text, image}:{
title: string;
text: string;
image: string;
}) {
    return (
        <div className="flex flex-col p-4 ">
            <div className="flex flex-row ">
                <img  className="w-12 h-12 " src={image} alt="Illustration" />
                <h1 className="font-bold text-3xl m-2 ">{title}</h1>
            </div>
            <p className=" whitespace-pre-line text-2xl leading-loose  ">{text}</p>
            

        </div>
    );

}
export default Soluce;