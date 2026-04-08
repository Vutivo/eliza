function Tags({ image, title }: { image?: string; title: string }){
  return (
    <div>
        <div className="flex  items-center justify-center gap-4">
            <img src={image} alt={title} className="w-8 h-8 rounded-full" />
            <h3 className="text-lg font-semibold text-gray-800">{title}</h3>
        </div>
    </div>
  );
}
export default Tags;