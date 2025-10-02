import { useParams } from "react-router-dom";

function Board() {
  const { id } = useParams();
  return (
    <div>
      <h1>Board {id}</h1>
    </div>
  );
}

export default Board;