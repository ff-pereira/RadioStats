import Body from "../components/Body.jsx";
import InvalidData from "../components/InvalidData.jsx";

export default function NotFoundPage() {
    return (
        <Body>
            <InvalidData title="Page" full={true}/>
        </Body>
    );
}