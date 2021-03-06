from pytest import mark, raises

from app.schemas.user import UserInsert, UserPatch, check_password


def test_password():
    with raises(ValueError) as error:
        check_password('1234')
    assert 'Password length' in str(error)

    with raises(ValueError) as error:
        check_password('1234123412341234')
    assert 'Variety <' in str(error)

    check_password('new password!!!')


@mark.parametrize('user_schema', [UserInsert, UserPatch])
def test_user_model(user_schema):
    with raises(ValueError):
        user_schema(
            name='abcdef',
            email='invalid.email.com',
            password='valid password!!!',
        )

    with raises(ValueError):
        user_schema(name='abcdef', email='valid@email.com', password='invalid')

    assert user_schema(
        name='abcdef', email='valid@email.com', password='valid password!!!'
    )
